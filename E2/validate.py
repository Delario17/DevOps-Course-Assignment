#!/usr/bin/env python3
"""Validate the A08-B08 E2 contract, examples, and cross-file invariants."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import warnings
from copy import deepcopy
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator
from urllib.parse import urlparse

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
    from openapi_spec_validator import validate as validate_openapi
except ImportError as error:  # pragma: no cover - exercised by a clean environment
    yaml = None
    Draft202012Validator = None
    FormatChecker = None
    SchemaError = ValueError
    validate_openapi = None
    VALIDATION_IMPORT_ERROR: ImportError | None = error
else:
    VALIDATION_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parent
VALID = ROOT / "examples" / "valid"
INVALID = ROOT / "examples" / "invalid"
ARTIFACTS = ROOT / "examples" / "artifacts"
ERROR_EXAMPLES = ROOT / "examples" / "errors"

JOB_TYPES = {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}
STATUSES = {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}
TERMINAL_ERRORS = {"FAILED", "TIMED_OUT", "CANCELLED"}
ERROR_CODES = {
    "CONTRACT_2001",
    "BASELINE_2002",
    "ENV_3001",
    "ENV_3002",
    "EXEC_4001",
    "EXEC_4002",
    "ANALYSIS_5001",
    "REPAIR_6001",
    "CANCELLED_7001",
}
RETRYABLE_ERROR_CODES = {"ENV_3001", "ENV_3002", "EXEC_4002", "ANALYSIS_5001"}
ARTIFACT_TYPES = {
    "DOCKERFILE",
    "CONTAINER_IMAGE",
    "BUILD_LOG_BUNDLE",
    "ACTUAL_GRAPH",
    "DECLARED_GRAPH",
    "ERROR_REPORT",
    "GIT_PATCH",
    "REPAIR_REPORT",
}


class ContractError(ValueError):
    pass


def fail(message: str) -> None:
    raise ContractError(message)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    ensure(isinstance(data, dict), f"{path}: root must be an object")
    return data


def load_yaml(path: Path) -> dict[str, Any]:
    ensure(yaml is not None, "validation dependencies are not installed")
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    ensure(isinstance(data, dict), f"{path}: root must be an object")
    return data


def require_validation_dependencies() -> None:
    if VALIDATION_IMPORT_ERROR is not None:
        fail(
            "missing validation dependencies; run "
            "`python3 -m pip install -r requirements.txt` "
            f"({VALIDATION_IMPORT_ERROR})"
        )


def validate_schema(schema: dict[str, Any], where: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        fail(f"{where}: invalid Draft 2020-12 schema: {error.message}")


def validate_instance(instance: Any, schema: dict[str, Any], where: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        fail(f"{where}{pointer}: {error.message}")


def expect_schema_rejected(label: str, instance: Any, schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if not list(validator.iter_errors(instance)):
        fail(f"{label}: invalid sample passed JSON Schema validation")
    print(f"[EXPECTED REJECTION] {label}: JSON Schema rejected the sample")


def positive_or_zero_integer(value: Any, where: str) -> int:
    ensure(type(value) is int and value >= 0, f"{where}: expected a non-negative integer")
    return value


def exact_keys(value: dict[str, Any], required: set[str], optional: set[str], where: str) -> None:
    missing = required - value.keys()
    extra = value.keys() - required - optional
    ensure(not missing, f"{where}: missing fields {sorted(missing)}")
    ensure(not extra, f"{where}: unexpected fields {sorted(extra)}")


def nonempty_string(value: Any, where: str) -> str:
    ensure(isinstance(value, str) and bool(value.strip()), f"{where}: expected non-empty string")
    return value


def fullmatch(pattern: str, value: Any, where: str) -> str:
    text = nonempty_string(value, where)
    ensure(re.fullmatch(pattern, text) is not None, f"{where}: invalid value {text!r}")
    return text


def valid_uri(value: Any, where: str, schemes: set[str]) -> str:
    text = nonempty_string(value, where)
    parsed = urlparse(text)
    ensure(parsed.scheme in schemes and bool(parsed.netloc), f"{where}: invalid URI {text!r}")
    return text


def validate_subject(subject: Any, where: str) -> None:
    ensure(isinstance(subject, dict), f"{where}: expected object")
    exact_keys(subject, {"repository_url", "commit", "configuration_id"}, set(), where)
    valid_uri(subject["repository_url"], f"{where}.repository_url", {"http", "https"})
    fullmatch(r"[a-f0-9]{40}", subject["commit"], f"{where}.commit")
    fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,63}", subject["configuration_id"], f"{where}.configuration_id")


def validate_environment(environment: Any, subject: dict[str, Any], where: str) -> None:
    ensure(isinstance(environment, dict), f"{where}: expected object")
    exact_keys(environment, {"container_image", "working_directory"}, set(), where)
    image = environment["container_image"]
    validate_artifact_ref(image, f"{where}.container_image", "CONTAINER_IMAGE")
    ensure(image["subject"] == subject, f"{where}: container image subject mismatch")
    ensure(urlparse(image["uri"]).scheme == "docker", f"{where}.container_image.uri: expected docker URI")
    working = nonempty_string(environment["working_directory"], f"{where}.working_directory")
    ensure(working.startswith("/"), f"{where}.working_directory: expected absolute path")


def validate_artifact_ref(ref: Any, where: str, expected_type: str | None = None) -> None:
    ensure(isinstance(ref, dict), f"{where}: expected object")
    exact_keys(
        ref,
        {"artifact_id", "type", "uri", "media_type", "producer_job_id", "subject"},
        {"sha256"},
        where,
    )
    fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", ref["artifact_id"], f"{where}.artifact_id")
    ensure(ref["type"] in ARTIFACT_TYPES, f"{where}.type: unsupported artifact type")
    if expected_type:
        ensure(ref["type"] == expected_type, f"{where}.type: expected {expected_type}")
    valid_uri(ref["uri"], f"{where}.uri", {"artifact", "http", "https", "docker"})
    nonempty_string(ref["media_type"], f"{where}.media_type")
    fullmatch(r"job-[a-z0-9-]{3,64}", ref["producer_job_id"], f"{where}.producer_job_id")
    validate_subject(ref["subject"], f"{where}.subject")
    if "sha256" in ref:
        fullmatch(r"[a-f0-9]{64}", ref["sha256"], f"{where}.sha256")


def validate_draft_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "context_documents", "build"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    docs = value["context_documents"]
    ensure(isinstance(docs, list) and len(docs) <= 2, f"{where}.context_documents: maximum two documents")
    for index, item in enumerate(docs):
        nonempty_string(item, f"{where}.context_documents[{index}]")
    build = value["build"]
    ensure(isinstance(build, dict), f"{where}.build: expected object")
    exact_keys(
        build,
        {"working_directory", "build_command", "verify_command", "max_iterations", "timeout_seconds"},
        {"base_image_hint"},
        f"{where}.build",
    )
    ensure(nonempty_string(build["working_directory"], f"{where}.build.working_directory").startswith("/"),
           f"{where}.build.working_directory: expected absolute path")
    nonempty_string(build["build_command"], f"{where}.build.build_command")
    nonempty_string(build["verify_command"], f"{where}.build.verify_command")
    ensure(type(build["max_iterations"]) is int and 1 <= build["max_iterations"] <= 50,
           f"{where}.build.max_iterations: expected 1..50")
    ensure(type(build["timeout_seconds"]) is int and 30 <= build["timeout_seconds"] <= 1800,
           f"{where}.build.timeout_seconds: expected 30..1800")


def validate_full_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "clean_build_command"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], value["subject"], f"{where}.environment")
    nonempty_string(value["clean_build_command"], f"{where}.clean_build_command")


def validate_incremental_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "baseline", "incremental_build_command"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], value["subject"], f"{where}.environment")
    baseline = value["baseline"]
    ensure(isinstance(baseline, dict), f"{where}.baseline: expected object")
    exact_keys(baseline, {"base_commit", "configuration_id", "actual_graph"}, set(), f"{where}.baseline")
    fullmatch(r"[a-f0-9]{40}", baseline["base_commit"], f"{where}.baseline.base_commit")
    nonempty_string(baseline["configuration_id"], f"{where}.baseline.configuration_id")
    validate_artifact_ref(baseline["actual_graph"], f"{where}.baseline.actual_graph", "ACTUAL_GRAPH")
    nonempty_string(value["incremental_build_command"], f"{where}.incremental_build_command")

    current_config = value["subject"]["configuration_id"]
    graph_subject = baseline["actual_graph"]["subject"]
    ensure(baseline["configuration_id"] == current_config, f"{where}: baseline configuration mismatch")
    ensure(graph_subject["configuration_id"] == current_config, f"{where}: graph configuration mismatch")
    ensure(graph_subject["repository_url"] == value["subject"]["repository_url"],
           f"{where}: graph repository does not match current repository")
    ensure(graph_subject["commit"] == baseline["base_commit"],
           f"{where}: graph commit does not match base_commit")


def validate_repair_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "md_report", "makefile_path", "validation"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], value["subject"], f"{where}.environment")
    validate_artifact_ref(value["md_report"], f"{where}.md_report", "ERROR_REPORT")
    makefile_text = nonempty_string(value["makefile_path"], f"{where}.makefile_path")
    makefile_path = PurePosixPath(makefile_text)
    ensure(not makefile_path.is_absolute() and ".." not in makefile_path.parts and "\\" not in makefile_text,
           f"{where}.makefile_path: expected a path inside the source tree")
    validation = value["validation"]
    ensure(isinstance(validation, dict), f"{where}.validation: expected object")
    exact_keys(validation, {"build_command", "test_command", "recheck_endpoint"}, set(), f"{where}.validation")
    nonempty_string(validation["build_command"], f"{where}.validation.build_command")
    nonempty_string(validation["test_command"], f"{where}.validation.test_command")
    ensure(nonempty_string(validation["recheck_endpoint"], f"{where}.validation.recheck_endpoint").startswith("/v1/"),
           f"{where}.validation.recheck_endpoint: expected /v1/ path")
    ensure(value["md_report"]["subject"] == value["subject"], f"{where}: report reference subject mismatch")


INPUT_VALIDATORS: dict[str, Callable[[dict[str, Any], str], None]] = {
    "DRAFT": validate_draft_input,
    "FULL_CHECK": validate_full_input,
    "INCREMENTAL_CHECK": validate_incremental_input,
    "REPAIR": validate_repair_input,
}


def validate_create_request(value: dict[str, Any], where: str) -> None:
    exact_keys(
        value,
        {"schema_version", "trace_id", "pair_id", "idempotency_key", "job_type", "input"},
        set(),
        where,
    )
    ensure(value["schema_version"] == "1.0.0", f"{where}.schema_version: expected 1.0.0")
    fullmatch(r"trace-[a-z0-9-]{3,64}", value["trace_id"], f"{where}.trace_id")
    ensure(value["pair_id"] == "A08-B08", f"{where}.pair_id: expected A08-B08")
    fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{7,127}", value["idempotency_key"], f"{where}.idempotency_key")
    ensure(value["job_type"] in JOB_TYPES, f"{where}.job_type: unsupported value {value['job_type']!r}")
    ensure(isinstance(value["input"], dict), f"{where}.input: expected object")
    INPUT_VALIDATORS[value["job_type"]](value["input"], f"{where}.input")


def validate_error_report(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"schema_version", "report_id", "subject", "detector", "findings"}, set(), where)
    ensure(value["schema_version"] == "1.0.0", f"{where}.schema_version: expected 1.0.0")
    fullmatch(r"report-[a-z0-9-]{3,64}", value["report_id"], f"{where}.report_id")
    validate_subject(value["subject"], f"{where}.subject")
    ensure(value["detector"] in {"BUILDCHECKER", "ECHECKER", "INSTRUCTOR_ORACLE"}, f"{where}.detector: unsupported")
    findings = value["findings"]
    ensure(isinstance(findings, list), f"{where}.findings: expected array")
    for index, finding in enumerate(findings):
        item = f"{where}.findings[{index}]"
        ensure(isinstance(finding, dict), f"{item}: expected object")
        exact_keys(
            finding,
            {"finding_id", "type", "target", "dependency", "build_file", "evidence"},
            {"line"},
            item,
        )
        fullmatch(r"finding-[a-z0-9-]{3,64}", finding["finding_id"], f"{item}.finding_id")
        ensure(finding["type"] in {"MISSING", "REDUNDANT"}, f"{item}.type: unsupported")
        for key in ("target", "dependency", "build_file"):
            nonempty_string(finding[key], f"{item}.{key}")
        if "line" in finding:
            ensure(type(finding["line"]) is int and finding["line"] >= 1, f"{item}.line: expected positive integer")
        ensure(isinstance(finding["evidence"], list) and finding["evidence"], f"{item}.evidence: expected non-empty array")
        for evidence_index, evidence in enumerate(finding["evidence"]):
            nonempty_string(evidence, f"{item}.evidence[{evidence_index}]")


def validate_repair_report_link(request: dict[str, Any], report: dict[str, Any], where: str) -> None:
    ensure(request["job_type"] == "REPAIR", f"{where}: expected REPAIR request")
    ensure(report["subject"] == request["input"]["subject"], f"{where}: report content subject mismatch")
    ensure(bool(report["findings"]), f"{where}: MDFixer requires at least one MISSING finding")
    non_missing = [item["finding_id"] for item in report["findings"] if item["type"] != "MISSING"]
    ensure(not non_missing, f"{where}: MDFixer only accepts MISSING findings; rejected {non_missing}")


def validate_artifact_record(value: dict[str, Any], where: str) -> None:
    required = {"schema_version", "artifact_id", "type", "uri", "media_type", "producer_job_id", "subject"}
    optional = {"sha256", "size_bytes", "created_at"}
    exact_keys(value, required, optional, where)
    ensure(value["schema_version"] == "1.0.0", f"{where}.schema_version: expected 1.0.0")
    validate_artifact_ref({key: value[key] for key in required - {"schema_version"} | ({"sha256"} if "sha256" in value else set())}, where)
    if "size_bytes" in value:
        ensure(type(value["size_bytes"]) is int and value["size_bytes"] >= 0, f"{where}.size_bytes: invalid")
    if "created_at" in value:
        datetime.fromisoformat(value["created_at"])


def validate_job_error(value: Any, where: str) -> None:
    ensure(isinstance(value, dict), f"{where}: expected object")
    exact_keys(value, {"code", "message", "retryable"}, {"details"}, where)
    ensure(value["code"] in ERROR_CODES, f"{where}.code: unsupported")
    nonempty_string(value["message"], f"{where}.message")
    ensure(isinstance(value["retryable"], bool), f"{where}.retryable: expected boolean")
    ensure(value["retryable"] is (value["code"] in RETRYABLE_ERROR_CODES),
           f"{where}.retryable: does not match the error-code policy")
    if "details" in value:
        ensure(isinstance(value["details"], dict), f"{where}.details: expected object")


def validate_problem(value: Any, where: str) -> None:
    ensure(isinstance(value, dict), f"{where}: expected object")
    exact_keys(value, {"code", "message", "trace_id"}, {"field"}, where)
    ensure(value["code"] in ERROR_CODES, f"{where}.code: unsupported")
    nonempty_string(value["message"], f"{where}.message")
    fullmatch(r"trace-[a-z0-9-]{3,64}", value["trace_id"], f"{where}.trace_id")
    if "field" in value:
        nonempty_string(value["field"], f"{where}.field")


def output_artifacts(output: dict[str, Any]) -> list[dict[str, Any]]:
    return [value for value in output.values() if isinstance(value, dict) and "artifact_id" in value]


def validate_job(value: dict[str, Any], where: str) -> None:
    required = {
        "schema_version", "job_id", "trace_id", "pair_id", "idempotency_key", "job_type",
        "status", "created_at", "updated_at", "input", "output", "error",
    }
    exact_keys(value, required, set(), where)
    request = {key: value[key] for key in ("schema_version", "trace_id", "pair_id", "idempotency_key", "job_type", "input")}
    validate_create_request(request, where)
    fullmatch(r"job-[a-z0-9-]{3,64}", value["job_id"], f"{where}.job_id")
    ensure(value["status"] in STATUSES, f"{where}.status: unsupported")
    created_at = datetime.fromisoformat(value["created_at"])
    updated_at = datetime.fromisoformat(value["updated_at"])
    ensure(updated_at >= created_at, f"{where}: updated_at precedes created_at")

    if value["status"] in {"QUEUED", "RUNNING"}:
        ensure(value["output"] is None and value["error"] is None, f"{where}: active job must have null output and error")
    elif value["status"] == "SUCCEEDED":
        ensure(isinstance(value["output"], dict) and value["error"] is None, f"{where}: successful job requires output and null error")
        validate_success_output(value, where)
    elif value["status"] in TERMINAL_ERRORS:
        ensure(value["output"] is None, f"{where}: failed terminal job must have null output")
        validate_job_error(value["error"], f"{where}.error")


def validate_success_output(job: dict[str, Any], where: str) -> None:
    output = job["output"]
    job_type = job["job_type"]
    subject = job["input"]["subject"]
    if job_type == "DRAFT":
        exact_keys(output, {"dockerfile", "container_image", "iteration_log", "build_verification"}, set(), f"{where}.output")
        validate_artifact_ref(output["dockerfile"], f"{where}.output.dockerfile", "DOCKERFILE")
        validate_artifact_ref(output["container_image"], f"{where}.output.container_image", "CONTAINER_IMAGE")
        validate_artifact_ref(output["iteration_log"], f"{where}.output.iteration_log", "BUILD_LOG_BUNDLE")
        ensure(urlparse(output["container_image"]["uri"]).scheme == "docker",
               f"{where}.output.container_image.uri: expected docker URI")
        verification = output["build_verification"]
        exact_keys(verification, {"build_exit_code", "verify_exit_code", "verdict"}, set(), f"{where}.output.build_verification")
        ensure(type(verification["build_exit_code"]) is int, f"{where}: build_exit_code must be an integer")
        ensure(type(verification["verify_exit_code"]) is int, f"{where}: verify_exit_code must be an integer")
        ensure(verification["build_exit_code"] == 0 and verification["verify_exit_code"] == 0,
               f"{where}: successful DRAFT requires zero build and verification exit codes")
        ensure(verification["verdict"] == "PASSED", f"{where}: successful DRAFT requires PASSED verdict")
    elif job_type == "FULL_CHECK":
        exact_keys(output, {"actual_graph", "declared_graph", "error_report", "summary"}, set(), f"{where}.output")
        validate_artifact_ref(output["actual_graph"], f"{where}.output.actual_graph", "ACTUAL_GRAPH")
        validate_artifact_ref(output["declared_graph"], f"{where}.output.declared_graph", "DECLARED_GRAPH")
        validate_artifact_ref(output["error_report"], f"{where}.output.error_report", "ERROR_REPORT")
        summary = output["summary"]
        ensure(isinstance(summary, dict), f"{where}.output.summary: expected object")
        exact_keys(summary, {"missing", "redundant"}, set(), f"{where}.output.summary")
        positive_or_zero_integer(summary["missing"], f"{where}.output.summary.missing")
        positive_or_zero_integer(summary["redundant"], f"{where}.output.summary.redundant")
    elif job_type == "INCREMENTAL_CHECK":
        exact_keys(output, {"updated_actual_graph", "error_report", "delta"}, set(), f"{where}.output")
        validate_artifact_ref(output["updated_actual_graph"], f"{where}.output.updated_actual_graph", "ACTUAL_GRAPH")
        validate_artifact_ref(output["error_report"], f"{where}.output.error_report", "ERROR_REPORT")
        delta = output["delta"]
        ensure(isinstance(delta, dict), f"{where}.output.delta: expected object")
        exact_keys(delta, {"added", "resolved", "unchanged"}, set(), f"{where}.output.delta")
        for key in ("added", "resolved", "unchanged"):
            positive_or_zero_integer(delta[key], f"{where}.output.delta.{key}")
    elif job_type == "REPAIR":
        exact_keys(output, {"patch", "repair_report", "declaration_style", "validation_result"}, set(), f"{where}.output")
        validate_artifact_ref(output["patch"], f"{where}.output.patch", "GIT_PATCH")
        validate_artifact_ref(output["repair_report"], f"{where}.output.repair_report", "REPAIR_REPORT")
        ensure(output["declaration_style"] in {"DEPENDENCY_LIST", "MACRO", "HYBRID", "IMPLICIT"}, f"{where}: invalid declaration style")
        result = output["validation_result"]
        exact_keys(result, {"build", "test", "recheck", "accepted"}, set(), f"{where}.output.validation_result")
        ensure(all(result[key] == "PASSED" for key in ("build", "test", "recheck")), f"{where}: accepted repair must pass all checks")
        ensure(result["accepted"] is True, f"{where}: successful repair must be accepted")
    else:
        fail(f"{where}: unsupported success output for {job_type}")

    for artifact in output_artifacts(output):
        ensure(artifact["subject"] == subject, f"{where}: output artifact subject mismatch")
        ensure(artifact["producer_job_id"] == job["job_id"], f"{where}: output artifact producer mismatch")


def synthetic_queued_job(request: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "schema_version": request["schema_version"],
        "job_id": f"job-synthetic-{index:02d}",
        "trace_id": request["trace_id"],
        "pair_id": request["pair_id"],
        "idempotency_key": request["idempotency_key"],
        "job_type": request["job_type"],
        "status": "QUEUED",
        "created_at": "2026-09-17T08:00:00+08:00",
        "updated_at": "2026-09-17T08:00:00+08:00",
        "input": request["input"],
        "output": None,
        "error": None,
    }


def expect_rejected(label: str, callback: Callable[[], None]) -> None:
    try:
        callback()
    except ContractError as error:
        print(f"[EXPECTED REJECTION] {label}: {error}")
        return
    fail(f"{label}: invalid sample was accepted")


ENDPOINT_JOB_TYPES = {
    "/v1/dockerfile-jobs": "DRAFT",
    "/v1/full-check-jobs": "FULL_CHECK",
    "/v1/incremental-check-jobs": "INCREMENTAL_CHECK",
    "/v1/repair-jobs": "REPAIR",
}


def validate_external_paths(value: Any, base: Path, where: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"$ref", "externalValue"} and isinstance(child, str):
                if not child.startswith("#") and "://" not in child:
                    relative = child.split("#", 1)[0]
                    ensure((base / relative).is_file(), f"{where}: missing referenced file {child}")
            validate_external_paths(child, base, where)
    elif isinstance(value, list):
        for child in value:
            validate_external_paths(child, base, where)


def validate_openapi_contract(document: dict[str, Any], path: Path) -> None:
    try:
        validate_openapi(document, base_uri=path.as_uri())
    except Exception as error:
        fail(f"{path.name}: invalid OpenAPI document: {error}")

    validate_external_paths(document, path.parent, path.name)
    for endpoint, expected_job_type in ENDPOINT_JOB_TYPES.items():
        try:
            schema = document["paths"][endpoint]["post"]["requestBody"]["content"]["application/json"]["schema"]
        except (KeyError, TypeError):
            fail(f"{path.name}: missing request schema for {endpoint}")
        clauses = schema.get("allOf", []) if isinstance(schema, dict) else []
        constants = {
            clause.get("properties", {}).get("job_type", {}).get("const")
            for clause in clauses
            if isinstance(clause, dict)
        }
        ensure(expected_job_type in constants,
               f"{path.name}: {endpoint} must constrain job_type to {expected_job_type}")

    try:
        accepted_schema = document["components"]["responses"]["AcceptedJob"]["content"]["application/json"]["schema"]
    except (KeyError, TypeError):
        fail(f"{path.name}: missing AcceptedJob response schema")
    clauses = accepted_schema.get("allOf", []) if isinstance(accepted_schema, dict) else []
    status_sets = {
        tuple(clause.get("properties", {}).get("status", {}).get("enum", []))
        for clause in clauses
        if isinstance(clause, dict)
    }
    ensure(("QUEUED", "RUNNING") in status_sets,
           f"{path.name}: AcceptedJob must restrict status to QUEUED or RUNNING")


def validate_repair_failure(job: dict[str, Any], where: str) -> None:
    ensure(job["job_type"] == "REPAIR" and job["status"] == "FAILED", f"{where}: expected failed REPAIR job")
    error = job["error"]
    ensure(error["code"] == "REPAIR_6001", f"{where}: expected REPAIR_6001")
    details = error.get("details")
    ensure(isinstance(details, dict), f"{where}.error.details: expected object")
    exact_keys(
        details,
        {"rejection_reason", "candidate_validation", "repair_report"},
        set(),
        f"{where}.error.details",
    )
    nonempty_string(details["rejection_reason"], f"{where}.error.details.rejection_reason")
    repair_report = details["repair_report"]
    validate_artifact_ref(repair_report, f"{where}.error.details.repair_report", "REPAIR_REPORT")
    ensure(repair_report["producer_job_id"] == job["job_id"], f"{where}: failure report producer mismatch")
    ensure(repair_report["subject"] == job["input"]["subject"], f"{where}: failure report subject mismatch")
    validation = details["candidate_validation"]
    ensure(isinstance(validation, dict), f"{where}.error.details.candidate_validation: expected object")
    exact_keys(validation, {"build", "test", "recheck"}, set(), f"{where}.error.details.candidate_validation")
    for key in ("build", "test", "recheck"):
        ensure(validation[key] in {"PASSED", "FAILED", "NOT_RUN"},
               f"{where}.error.details.candidate_validation.{key}: unsupported value")
    ensure("FAILED" in validation.values(), f"{where}: rejected candidate must contain a failed validation")


def validate_draft_failure(job: dict[str, Any], where: str) -> None:
    ensure(job["job_type"] == "DRAFT" and job["status"] == "FAILED", f"{where}: expected failed DRAFT job")
    details = job["error"].get("details")
    ensure(isinstance(details, dict), f"{where}.error.details: expected object")
    exact_keys(details, {"last_stage", "log"}, set(), f"{where}.error.details")
    nonempty_string(details["last_stage"], f"{where}.error.details.last_stage")
    log = details["log"]
    validate_artifact_ref(log, f"{where}.error.details.log", "BUILD_LOG_BUNDLE")
    ensure(log["producer_job_id"] == job["job_id"], f"{where}: failure log producer mismatch")
    ensure(log["subject"] == job["input"]["subject"], f"{where}: failure log subject mismatch")


def artifact_uri_references(
    value: Any,
    where: str,
) -> Iterator[tuple[str, str | None, str | None, dict[str, Any] | None, str]]:
    """Yield artifact URI, digest, type, subject, and JSON location."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_where = f"{where}.{key}"
            if isinstance(child, str) and child.startswith("artifact://"):
                ref_keys = {
                    "artifact_id", "type", "uri", "media_type", "producer_job_id", "subject"
                }
                ensure(key == "uri" and ref_keys <= value.keys(),
                       f"{child_where}: artifact URI must be carried by a complete ArtifactRef")
                ref = {name: value[name] for name in ref_keys}
                if "sha256" in value:
                    ref["sha256"] = value["sha256"]
                validate_artifact_ref(ref, where)
                digest = value.get("sha256")
                artifact_type = value.get("type")
                subject = value.get("subject")
                yield child, digest, artifact_type, subject, child_where
            yield from artifact_uri_references(child, child_where)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from artifact_uri_references(child, f"{where}[{index}]")


def artifact_uri_path(uri: str, where: str) -> Path:
    parsed = urlparse(uri)
    ensure(parsed.scheme == "artifact" and parsed.netloc == "a08-b08", f"{where}: unsupported artifact authority")
    ensure(not parsed.query and not parsed.fragment, f"{where}: query and fragment are not allowed")
    relative = PurePosixPath(parsed.path.removeprefix("/"))
    ensure(relative.parts and all(part not in {"", ".", ".."} for part in relative.parts),
           f"{where}: unsafe artifact path")
    return ARTIFACTS / parsed.netloc / Path(*relative.parts)


def validate_graph_content(value: dict[str, Any], where: str, artifact_type: str) -> None:
    exact_keys(
        value,
        {"schema_version", "graph_id", "graph_type", "producer_job_id", "subject", "nodes", "edges"},
        set(),
        where,
    )
    ensure(value["schema_version"] == "1.0.0", f"{where}.schema_version: expected 1.0.0")
    expected_graph_type = "DECLARED" if artifact_type == "DECLARED_GRAPH" else "ACTUAL"
    ensure(value["graph_type"] == expected_graph_type, f"{where}.graph_type: expected {expected_graph_type}")
    nonempty_string(value["graph_id"], f"{where}.graph_id")
    fullmatch(r"job-[a-z0-9-]{3,64}", value["producer_job_id"], f"{where}.producer_job_id")
    validate_subject(value["subject"], f"{where}.subject")
    ensure(isinstance(value["nodes"], list), f"{where}.nodes: expected array")
    ensure(isinstance(value["edges"], list), f"{where}.edges: expected array")


def validate_materialized_artifacts(schemas: dict[str, dict[str, Any]]) -> int:
    sources = sorted(VALID.glob("*.json")) + [
        ARTIFACTS / "md-report.artifact.json",
        INVALID / "repair-redundant-report.request.json",
    ]
    references: dict[str, tuple[str | None, str | None, dict[str, Any] | None, str]] = {}
    for source in sources:
        document = load(source)
        source_where = str(source.relative_to(ROOT))
        for uri, digest, artifact_type, subject, where in artifact_uri_references(document, source_where):
            previous = references.get(uri)
            if previous and digest and previous[0]:
                ensure(digest == previous[0], f"{where}: conflicting SHA-256 for {uri}")
            references[uri] = (
                digest or (previous[0] if previous else None),
                artifact_type or (previous[1] if previous else None),
                subject or (previous[2] if previous else None),
                where,
            )

    for uri, (digest, artifact_type, subject, where) in sorted(references.items()):
        path = artifact_uri_path(uri, where)
        ensure(path.is_file(), f"{where}: {uri} does not resolve to a local sample")
        if digest:
            actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            ensure(actual_digest == digest, f"{where}: SHA-256 does not match {path.relative_to(ROOT)}")

        if path.suffix == ".json":
            content = load(path)
            content_where = str(path.relative_to(ROOT))
            if subject is not None and "subject" in content:
                ensure(content["subject"] == subject, f"{content_where}: subject does not match ArtifactRef")
            if artifact_type == "ERROR_REPORT":
                validate_instance(content, schemas["error-report.schema.json"], content_where)
                validate_error_report(content, content_where)
            elif artifact_type == "REPAIR_REPORT":
                validate_instance(content, schemas["repair-report.schema.json"], content_where)
            elif artifact_type == "BUILD_LOG_BUNDLE":
                validate_instance(content, schemas["draft-manifest.schema.json"], content_where)
            elif artifact_type in {"ACTUAL_GRAPH", "DECLARED_GRAPH"}:
                validate_graph_content(content, content_where, artifact_type)
            elif artifact_type is None and path.name == "report.json" and path.parent.name.startswith("repair-"):
                validate_instance(content, schemas["repair-report.schema.json"], content_where)
        else:
            ensure(path.stat().st_size > 0, f"{path.relative_to(ROOT)}: artifact must not be empty")

    mirrors = {
        ARTIFACTS / "md-report.json": ARTIFACTS / "a08-b08/full-001/error-report.json",
        ARTIFACTS / "redundant-report.json": ARTIFACTS / "a08-b08/full-001/redundant-report.json",
        ARTIFACTS / "draft-manifest.json": ARTIFACTS / "a08-b08/draft-001/iterations.json",
        ARTIFACTS / "repair-report.json": ARTIFACTS / "a08-b08/repair-001/report.json",
    }
    for mirror, canonical in mirrors.items():
        ensure(mirror.read_bytes() == canonical.read_bytes(),
               f"{mirror.relative_to(ROOT)}: content differs from {canonical.relative_to(ROOT)}")

    return len(references)


def main() -> int:
    require_validation_dependencies()

    schema_files = sorted((ROOT / "contracts").glob("*.schema.json"))
    schemas: dict[str, dict[str, Any]] = {}
    for path in schema_files:
        schema = load(path)
        ensure(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{path}: wrong draft")
        ensure("$id" in schema and "title" in schema, f"{path}: missing schema metadata")
        validate_schema(schema, str(path.relative_to(ROOT)))
        schemas[path.name] = schema
        print(f"[PASS] Draft 2020-12 schema: {path.relative_to(ROOT)}")

    create_schema = schemas["create-request.schema.json"]
    task_schema = schemas["task.schema.json"]
    artifact_schema = schemas["artifact.schema.json"]
    error_report_schema = schemas["error-report.schema.json"]

    valid_requests = sorted(VALID.glob("*.request.json"))
    for index, path in enumerate(valid_requests, 1):
        request = load(path)
        validate_instance(request, create_schema, str(path.relative_to(ROOT)))
        validate_create_request(request, str(path.relative_to(ROOT)))
        queued_job = synthetic_queued_job(request, index)
        validate_instance(queued_job, task_schema, f"synthetic job for {path.name}")
        validate_job(queued_job, f"synthetic job for {path.name}")
        print(f"[PASS] request and queued response: {path.name}")

    job_files = sorted(path for path in VALID.glob("*.json") if not path.name.endswith(".request.json"))
    for path in job_files:
        job = load(path)
        job_where = str(path.relative_to(ROOT))
        validate_instance(job, task_schema, job_where)
        validate_job(job, job_where)
        if job["job_type"] == "REPAIR":
            report_ref = job["input"]["md_report"]
            report_path = artifact_uri_path(report_ref["uri"], f"{job_where}.input.md_report.uri")
            report = load(report_path)
            validate_instance(report, error_report_schema, str(report_path.relative_to(ROOT)))
            validate_error_report(report, str(report_path.relative_to(ROOT)))
            validate_repair_report_link(job, report, job_where)
        if job["job_type"] == "FULL_CHECK" and job["status"] == "SUCCEEDED":
            report_ref = job["output"]["error_report"]
            report_path = artifact_uri_path(report_ref["uri"], f"{job_where}.output.error_report.uri")
            report = load(report_path)
            validate_instance(report, error_report_schema, str(report_path.relative_to(ROOT)))
            validate_error_report(report, str(report_path.relative_to(ROOT)))
            expected_summary = {
                "missing": sum(item["type"] == "MISSING" for item in report["findings"]),
                "redundant": sum(item["type"] == "REDUNDANT" for item in report["findings"]),
            }
            ensure(job["output"]["summary"] == expected_summary,
                   f"{job_where}.output.summary: does not match the referenced report")
        if path.name == "draft.failed.json":
            validate_draft_failure(job, job_where)
        elif path.name == "repair.failed.json":
            validate_repair_failure(job, job_where)
        print(f"[PASS] job response: {path.name}")

    report_paths = [ARTIFACTS / name for name in ("md-report.json", "redundant-report.json", "clean-report.json")]
    reports: dict[str, dict[str, Any]] = {}
    for path in report_paths:
        report = load(path)
        validate_instance(report, error_report_schema, str(path.relative_to(ROOT)))
        validate_error_report(report, str(path.relative_to(ROOT)))
        reports[path.name] = report
    print("[PASS] dependency reports, including an empty clean report")

    artifact_records = sorted(ARTIFACTS.glob("*.artifact.json"))
    for path in artifact_records:
        metadata = load(path)
        validate_instance(metadata, artifact_schema, str(path.relative_to(ROOT)))
        validate_artifact_record(metadata, str(path.relative_to(ROOT)))
    metadata = load(ARTIFACTS / "md-report.artifact.json")
    digest = hashlib.sha256((ARTIFACTS / "md-report.json").read_bytes()).hexdigest()
    ensure(metadata["sha256"] == digest, "md-report.artifact.json: sha256 does not match content")
    ensure(metadata.get("size_bytes") == (ARTIFACTS / "md-report.json").stat().st_size,
           "md-report.artifact.json: size_bytes does not match content")
    producer_job = load(VALID / "full-check.succeeded.json")
    artifact_created_at = datetime.fromisoformat(metadata["created_at"])
    ensure(datetime.fromisoformat(producer_job["created_at"]) <= artifact_created_at
           <= datetime.fromisoformat(producer_job["updated_at"]),
           "md-report.artifact.json: created_at is outside the producer job lifetime")
    print("[PASS] artifact metadata, size, and sha256")

    manifest = load(ARTIFACTS / "draft-manifest.json")
    validate_instance(manifest, schemas["draft-manifest.schema.json"], "examples/artifacts/draft-manifest.json")
    repair_report = load(ARTIFACTS / "repair-report.json")
    validate_instance(repair_report, schemas["repair-report.schema.json"], "examples/artifacts/repair-report.json")
    print("[PASS] DRAFT manifest and repair report content schemas")

    artifact_uri_count = validate_materialized_artifacts(schemas)
    print(f"[PASS] {artifact_uri_count} artifact URI mappings, content bindings, and SHA-256 values")

    repair_request = load(VALID / "repair.request.json")
    validate_repair_report_link(repair_request, reports["md-report.json"], "repair.request.json")
    print("[PASS] repair request consumes matching MISSING report")

    bad_type = load(INVALID / "bad-job-type.request.json")
    expect_schema_rejected("unsupported job_type", bad_type, create_schema)
    expect_rejected("unsupported job_type", lambda: validate_create_request(bad_type, "bad-job-type.request.json"))

    missing_baseline = load(INVALID / "incremental-missing-baseline.request.json")
    expect_schema_rejected("incremental request without baseline", missing_baseline, create_schema)
    expect_rejected("incremental request without baseline", lambda: validate_create_request(missing_baseline, "incremental-missing-baseline.request.json"))

    rd_request = load(INVALID / "repair-redundant-report.request.json")
    validate_instance(rd_request, create_schema, "repair-redundant-report.request.json")
    validate_create_request(rd_request, "repair-redundant-report.request.json")
    expect_rejected(
        "MDFixer request containing REDUNDANT finding",
        lambda: validate_repair_report_link(rd_request, reports["redundant-report.json"], "repair-redundant-report.request.json"),
    )
    expect_rejected(
        "MDFixer request containing no findings",
        lambda: validate_repair_report_link(repair_request, reports["clean-report.json"], "repair.request.json"),
    )

    boolean_limit = load(INVALID / "draft-boolean-limit.request.json")
    expect_schema_rejected("boolean max_iterations", boolean_limit, create_schema)
    expect_rejected("boolean max_iterations", lambda: validate_create_request(boolean_limit, "draft-boolean-limit.request.json"))

    cross_repository = load(INVALID / "incremental-cross-repository.request.json")
    validate_instance(cross_repository, create_schema, "incremental-cross-repository.request.json")
    expect_rejected(
        "cross-repository incremental baseline",
        lambda: validate_create_request(cross_repository, "incremental-cross-repository.request.json"),
    )

    unsafe_makefile = load(INVALID / "repair-unsafe-makefile.request.json")
    expect_schema_rejected("Makefile path escapes source tree", unsafe_makefile, create_schema)
    expect_rejected(
        "Makefile path escapes source tree",
        lambda: validate_create_request(unsafe_makefile, "repair-unsafe-makefile.request.json"),
    )

    contradictory_draft = deepcopy(load(VALID / "draft.succeeded.json"))
    contradictory_draft["output"]["build_verification"]["verdict"] = "FAILED"
    expect_schema_rejected("SUCCEEDED DRAFT with failed verdict", contradictory_draft, task_schema)
    expect_rejected(
        "SUCCEEDED DRAFT with failed verdict",
        lambda: validate_job(contradictory_draft, "contradictory DRAFT job"),
    )

    openapi_path = ROOT / "openapi.yaml"
    openapi_document = load_yaml(openapi_path)
    validate_openapi_contract(openapi_document, openapi_path)
    problem_schema = openapi_document["components"]["schemas"]["Problem"]
    error_files = sorted(ERROR_EXAMPLES.glob("*.json"))
    ensure(len(error_files) >= 3, "examples/errors: expected HTTP 400, 409, and 422 examples")
    for path in error_files:
        problem = load(path)
        validate_instance(problem, problem_schema, str(path.relative_to(ROOT)))
        validate_problem(problem, str(path.relative_to(ROOT)))
    print("[PASS] OpenAPI structure, endpoint job types, references, and Problem examples")

    print(
        f"\nAll checks passed: {len(schema_files)} schemas, {len(valid_requests)} request types, "
        f"{len(job_files)} persisted job responses, {len(error_files)} HTTP errors, "
        f"{artifact_uri_count} materialized artifacts, and 8 rejection scenarios (13 rejection assertions)."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        raise SystemExit(1)
