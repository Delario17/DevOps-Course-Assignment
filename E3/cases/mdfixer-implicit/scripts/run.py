#!/usr/bin/env python3
"""Verify the E3 IMPLICIT reference repair in a disposable Linux directory."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[2]
FIXTURE = CASE / "fixture"
ORACLE = CASE / "oracle/expected.json"
PATCH = CASE / "patches/reference.patch"
INVALID_PATCH = CASE / "patches/invalid.patch"
TZ = dt.timezone(dt.timedelta(hours=8))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Run in Linux/Ubuntu WSL, not Windows Python or MinGW.")

    started = dt.datetime.now(TZ)
    output = (args.output or CASE / "evidence" / started.strftime("%Y%m%dT%H%M%S%f+0800")).resolve()
    if output in {ROOT, CASE, FIXTURE} or FIXTURE in output.parents:
        parser.error("Evidence must not be inside the source fixture.")
    output.mkdir(parents=True, exist_ok=False)
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    transcript = output / "commands.txt"
    record = {
        "schema_version": "e3-mdfixer-evidence-v1",
        "started_at": started.isoformat(),
        "operator": args.operator,
        "provenance": "REAL_LINUX_REFERENCE_PATCH_EXPERIMENT",
        "review_status": "PENDING_HUMAN_REVIEW",
        "subject": oracle["subject"],
        "declaration_style": "IMPLICIT",
        "not_a_detector_report": True,
        "not_an_mdfixer_output": True,
        "status": "RUNNING",
        "commands": [], "assertions": [], "stages": {}, "edits": [],
        "runner_sha256": digest(Path(__file__)),
        "oracle_sha256": digest(ORACLE),
        "reference_patch_sha256": digest(PATCH),
        "invalid_patch_sha256": digest(INVALID_PATCH),
        "platform": platform.platform(), "architecture": platform.machine(),
    }
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}

    def log(text: str) -> None:
        with transcript.open("a", encoding="utf-8") as stream:
            stream.write(text)

    def run(argv, cwd: Path, label: str, allow_failure=False):
        result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env, text=True,
                                encoding="utf-8", errors="replace", capture_output=True, timeout=120)
        record["commands"].append({"label": label, "argv": [str(x) for x in argv],
                                   "cwd": str(cwd), "exit_code": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        log(f"\n[{label}]\n$ cd {shlex.quote(str(cwd))}\n$ {shlex.join([str(x) for x in argv])}\n"
            f"{result.stdout}{result.stderr}\nexit_code={result.returncode}\n")
        if result.returncode and not allow_failure:
            raise RuntimeError(f"{label}: command failed with exit code {result.returncode}")
        return result

    def check(name: str, condition: bool) -> None:
        record["assertions"].append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    def stage(work: Path, name: str, build=None):
        version = run(["./bin/demo", "--version"], work, name + ":version").stdout.strip()
        behavior = int(run(["./bin/demo"], work, name + ":behavior").stdout.strip())
        check(name + ":version", version == "implicit-demo 1.0.0")
        check(name + ":behavior", behavior == oracle["expected_behavior"][name])
        snapshot = {
            "version_output": version, "behavior_output": behavior,
            "files": {p: {"sha256": digest(work / p), "mtime_ns": (work / p).stat().st_mtime_ns}
                      for p in ["build/main.o", "bin/demo"]},
        }
        if build is not None:
            snapshot["build_stdout"] = build.stdout
        record["stages"][name] = snapshot
        return snapshot

    def edit_value(work: Path, old: int, new: int) -> None:
        obj = work / "build/main.o"
        time.sleep(max(0, obj.stat().st_mtime + 1.1 - time.time()))
        header = work / "include/config.h"
        text = header.read_text(encoding="utf-8")
        check(f"CONFIG_VALUE {old} exists", text.count(f"#define CONFIG_VALUE {old}\n") == 1)
        header.write_text(text.replace(f"#define CONFIG_VALUE {old}\n", f"#define CONFIG_VALUE {new}\n"), encoding="utf-8")
        check(f"CONFIG_VALUE {new} newer than object", header.stat().st_mtime_ns > obj.stat().st_mtime_ns)
        record["edits"].append({"file": "include/config.h", "old": old, "new": new})
        log(f"EDIT include/config.h: CONFIG_VALUE {old} -> {new}\n")

    try:
        for tool in ["gcc", "make", "git", "python3"]:
            if not shutil.which(tool):
                raise RuntimeError(f"Required tool missing: {tool}")
        source_hashes = {p.relative_to(FIXTURE).as_posix(): digest(p)
                         for p in sorted(FIXTURE.rglob("*")) if p.is_file()}
        record["source_sha256"] = source_hashes
        check("fixture matches immutable SHA-256 manifest", source_hashes == oracle["source_sha256"])
        check("oracle declares IMPLICIT style", oracle["declaration_style"] == "IMPLICIT")
        check("oracle contains one MD", len(oracle["findings"]) == 1 and oracle["findings"][0]["type"] == "MISSING")
        record["workspace_commit"] = run(["git", "rev-parse", "HEAD"], ROOT, "workspace commit").stdout.strip()
        record["environment"] = {tool: run([tool, "--version"], ROOT, tool + " version").stdout
                                 for tool in ["gcc", "make", "git", "python3"]}
        (output / "input").mkdir()
        for source, name in [(ORACLE, "md-report.json"), (PATCH, "reference.patch"),
                             (INVALID_PATCH, "invalid.patch"), (FIXTURE / "Makefile", "Makefile.before")]:
            shutil.copy2(source, output / "input" / name)

        with tempfile.TemporaryDirectory(prefix="b08-e3-implicit-") as temporary:
            work = Path(temporary) / "sample"
            shutil.copytree(FIXTURE, work, ignore=shutil.ignore_patterns("build", "bin"))
            initial = stage(work, "initial", run(["make", "-j2"], work, "before:build"))
            compiler_deps = run(["gcc", "-MM", "-Iinclude", "-MT", "build/main.o", "src/main.c"], work, "compiler dependencies").stdout
            check("compiler sees config.h", "include/config.h" in compiler_deps)
            database = run(["make", "-np", "build/main.o"], work, "before:Make database").stdout
            rule = next(line for line in database.splitlines() if line.startswith("build/%.o: src/%.c"))
            check("pattern rule omits config.h", "include/config.h" not in rule)
            edit_value(work, 4, 5)
            stale = stage(work, "before_fix_config_4_to_5_incremental", run(["make", "-j2"], work, "before:incremental"))
            check("missing dependency leaves products unchanged", stale["files"] == initial["files"])
            run(["make", "clean"], work, "before:clean")
            stage(work, "before_fix_config_4_to_5_clean", run(["make", "-j2"], work, "before:clean build"))
            edit_value(work, 5, 4)
            run(["git", "apply", "--check", PATCH], work, "reference:patch check")
            run(["git", "apply", PATCH], work, "reference:patch apply")
            accepted_makefile = (work / "Makefile").read_bytes()
            (output / "input/Makefile.reference").write_bytes(accepted_makefile)
            run(["make", "clean"], work, "reference:clean")
            fixed = stage(work, "after_fix_config_4_clean", run(["make", "-j2"], work, "reference:build"))
            database = run(["make", "-np", "build/main.o"], work, "reference:Make database").stdout
            rule = next(line for line in database.splitlines() if line.startswith("build/%.o: src/%.c"))
            check("reference repairs implicit pattern rule", "include/config.h" in rule)
            edit_value(work, 4, 5)
            changed = stage(work, "after_fix_config_4_to_5_incremental", run(["make", "-j2"], work, "reference:first incremental"))
            check("first edit recompiles", "-c src/main.c -o build/main.o" in changed["build_stdout"] and changed["files"] != fixed["files"])
            edit_value(work, 5, 6)
            changed_again = stage(work, "after_fix_config_5_to_6_incremental", run(["make", "-j2"], work, "reference:second incremental"))
            check("second edit recompiles", "-c src/main.c -o build/main.o" in changed_again["build_stdout"] and changed_again["files"] != changed["files"])
            record["reference_decision"] = {"decision": "ACCEPTED", "build": "PASSED", "incremental_function": "PASSED", "md_recheck": "PASSED"}
            try:
                run(["git", "apply", "--check", INVALID_PATCH], work, "invalid:patch check")
                run(["git", "apply", INVALID_PATCH], work, "invalid:patch apply")
                (output / "input/Makefile.invalid").write_bytes((work / "Makefile").read_bytes())
                failed = run(["make", "-B", "-j2"], work, "invalid:forced build", allow_failure=True)
                check("invalid candidate exits nonzero", failed.returncode != 0)
                record["invalid_candidate"] = {"decision": "REJECTED", "build_exit_code": failed.returncode}
            finally:
                (work / "Makefile").write_bytes(accepted_makefile)
                log("RESTORE Makefile: last accepted reference bytes\n")
            check("rollback restores accepted Makefile", (work / "Makefile").read_bytes() == accepted_makefile)
            run(["make", "clean"], work, "rollback:clean")
            stage(work, "restored_output", run(["make", "-j2"], work, "rollback:build"))
        check("repository fixture unchanged", source_hashes == {p.relative_to(FIXTURE).as_posix(): digest(p) for p in sorted(FIXTURE.rglob("*")) if p.is_file()})
        record["status"] = "PASS"
    except Exception as error:
        record["status"] = "FAIL"
        record["error"] = f"{type(error).__name__}: {error}"
    finally:
        record["finished_at"] = dt.datetime.now(TZ).isoformat()
        dump(output / "observations.json", record)
        if "reference_decision" in record:
            dump(output / "reference-validation.json", record["reference_decision"])
        if "invalid_candidate" in record:
            dump(output / "rejected-candidate.json", record["invalid_candidate"])
        passed = sum(item["passed"] for item in record["assertions"])
        rows = "\n".join(f"| {name} | {value['behavior_output']} |" for name, value in record["stages"].items())
        (output / "README.md").write_text(
            f"# MDFixer IMPLICIT actual run\n\n- Operator: {args.operator}.\n- Started: {started.isoformat()}.\n"
            f"- Result: **{record['status']}**, {passed}/{len(record['assertions'])} assertions passed.\n\n"
            f"| Stage | Output |\n|---|---|\n{rows}\n\nThis validates a known reference patch, candidate rejection, and rollback; it is not MDFixer service output.\n",
            encoding="utf-8")
    print(f"{record['status']}\nASSERTIONS={passed}/{len(record['assertions'])}\nEVIDENCE_DIR={output}")
    if record["status"] != "PASS":
        print(record.get("error", "See observations.json"))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
