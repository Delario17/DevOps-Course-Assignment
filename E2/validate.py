#!/usr/bin/env python3
"""Validate the A08-B08 E2 contract examples with the Python standard library."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
VALID = ROOT / "examples" / "valid"
INVALID = ROOT / "examples" / "invalid"
ARTIFACTS = ROOT / "examples" / "artifacts"

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


def validate_environment(environment: Any, where: str) -> None:
    ensure(isinstance(environment, dict), f"{where}: expected object")
    exact_keys(environment, {"image_ref", "working_directory"}, set(), where)
    nonempty_string(environment["image_ref"], f"{where}.image_ref")
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
    ensure(isinstance(build["max_iterations"], int) and 1 <= build["max_iterations"] <= 50,
           f"{where}.build.max_iterations: expected 1..50")
    ensure(isinstance(build["timeout_seconds"], int) and 30 <= build["timeout_seconds"] <= 1800,
           f"{where}.build.timeout_seconds: expected 30..1800")


def validate_full_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "clean_build_command"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], f"{where}.environment")
    nonempty_string(value["clean_build_command"], f"{where}.clean_build_command")


def validate_incremental_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "baseline", "incremental_build_command"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], f"{where}.environment")
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
    ensure(graph_subject["base_commit" if "base_commit" in graph_subject else "commit"] == baseline["base_commit"],
           f"{where}: graph commit does not match base_commit")


def validate_repair_input(value: dict[str, Any], where: str) -> None:
    exact_keys(value, {"subject", "environment", "md_report", "makefile_path", "validation"}, set(), where)
    validate_subject(value["subject"], f"{where}.subject")
    validate_environment(value["environment"], f"{where}.environment")
    validate_artifact_ref(value["md_report"], f"{where}.md_report", "ERROR_REPORT")
    nonempty_string(value["makefile_path"], f"{where}.makefile_path")
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
    ensure(isinstance(findings, list) and findings, f"{where}.findings: expected non-empty array")
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
            ensure(isinstance(finding["line"], int) and finding["line"] >= 1, f"{item}.line: expected positive integer")
        ensure(isinstance(finding["evidence"], list) and finding["evidence"], f"{item}.evidence: expected non-empty array")


def validate_repair_report_link(request: dict[str, Any], report: dict[str, Any], where: str) -> None:
    ensure(request["job_type"] == "REPAIR", f"{where}: expected REPAIR request")
    ensure(report["subject"] == request["input"]["subject"], f"{where}: report content subject mismatch")
    non_missing = [item["finding_id"] for item in report["findings"] if item["type"] != "MISSING"]
    ensure(not non_missing, f"{where}: MDFixer only accepts MISSING findings; rejected {non_missing}")


def validate_artifact_record(value: dict[str, Any], where: str) -> None:
    required = {"schema_version", "artifact_id", "type", "uri", "media_type", "producer_job_id", "subject"}
    optional = {"sha256", "size_bytes", "created_at"}
    exact_keys(value, required, optional, where)
    ensure(value["schema_version"] == "1.0.0", f"{where}.schema_version: expected 1.0.0")
    validate_artifact_ref({key: value[key] for key in required - {"schema_version"} | ({"sha256"} if "sha256" in value else set())}, where)
    if "size_bytes" in value:
        ensure(isinstance(value["size_bytes"], int) and value["size_bytes"] >= 0, f"{where}.size_bytes: invalid")
    if "created_at" in value:
        datetime.fromisoformat(value["created_at"])


def validate_job_error(value: Any, where: str) -> None:
    ensure(isinstance(value, dict), f"{where}: expected object")
    exact_keys(value, {"code", "message", "retryable"}, {"details"}, where)
    ensure(value["code"] in ERROR_CODES, f"{where}.code: unsupported")
    nonempty_string(value["message"], f"{where}.message")
    ensure(isinstance(value["retryable"], bool), f"{where}.retryable: expected boolean")
    if "details" in value:
        ensure(isinstance(value["details"], dict), f"{where}.details: expected object")


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
    datetime.fromisoformat(value["created_at"])
    datetime.fromisoformat(value["updated_at"])

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
        verification = output["build_verification"]
        exact_keys(verification, {"build_exit_code", "verify_exit_code", "verdict"}, set(), f"{where}.output.build_verification")
        ensure(verification["verdict"] in {"PASSED", "FAILED"}, f"{where}: invalid verdict")
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
        fail(f"{where}: no persisted success sample is defined for {job_type}")

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


def main() -> int:
    schema_files = sorted((ROOT / "contracts").glob("*.schema.json"))
    for path in schema_files:
        schema = load(path)
        ensure(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{path}: wrong draft")
        ensure("$id" in schema and "title" in schema, f"{path}: missing schema metadata")
        print(f"[PASS] schema parsed: {path.relative_to(ROOT)}")

    valid_requests = sorted(VALID.glob("*.request.json"))
    for index, path in enumerate(valid_requests, 1):
        request = load(path)
        validate_create_request(request, str(path.relative_to(ROOT)))
        validate_job(synthetic_queued_job(request, index), f"synthetic job for {path.name}")
        print(f"[PASS] request and queued response: {path.name}")

    job_files = sorted(path for path in VALID.glob("*.json") if not path.name.endswith(".request.json"))
    for path in job_files:
        validate_job(load(path), str(path.relative_to(ROOT)))
        print(f"[PASS] job response: {path.name}")

    md_report = load(ARTIFACTS / "md-report.json")
    rd_report = load(ARTIFACTS / "redundant-report.json")
    validate_error_report(md_report, "md-report.json")
    validate_error_report(rd_report, "redundant-report.json")
    print("[PASS] dependency reports")

    metadata = load(ARTIFACTS / "md-report.artifact.json")
    validate_artifact_record(metadata, "md-report.artifact.json")
    digest = hashlib.sha256((ARTIFACTS / "md-report.json").read_bytes()).hexdigest()
    ensure(metadata["sha256"] == digest, "md-report.artifact.json: sha256 does not match content")
    print("[PASS] artifact metadata and sha256")

    repair_request = load(VALID / "repair.request.json")
    validate_repair_report_link(repair_request, md_report, "repair.request.json")
    print("[PASS] repair request consumes matching MISSING report")

    bad_type = load(INVALID / "bad-job-type.request.json")
    expect_rejected("unsupported job_type", lambda: validate_create_request(bad_type, "bad-job-type.request.json"))

    missing_baseline = load(INVALID / "incremental-missing-baseline.request.json")
    expect_rejected("incremental request without baseline", lambda: validate_create_request(missing_baseline, "incremental-missing-baseline.request.json"))

    rd_request = load(INVALID / "repair-redundant-report.request.json")
    validate_create_request(rd_request, "repair-redundant-report.request.json")
    expect_rejected("MDFixer request containing REDUNDANT finding", lambda: validate_repair_report_link(rd_request, rd_report, "repair-redundant-report.request.json"))

    openapi_text = (ROOT / "openapi.yaml").read_text(encoding="utf-8")
    for endpoint in (
        "/v1/dockerfile-jobs",
        "/v1/full-check-jobs",
        "/v1/incremental-check-jobs",
        "/v1/repair-jobs",
        "/v1/jobs/{job_id}",
    ):
        ensure(endpoint in openapi_text, f"openapi.yaml: missing {endpoint}")
    print("[PASS] OpenAPI contains four create endpoints and the query endpoint")

    print(f"\nAll checks passed: {len(valid_requests)} request types, {len(job_files)} persisted job responses, 3 expected rejections.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        raise SystemExit(1)
