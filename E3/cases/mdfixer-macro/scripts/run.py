#!/usr/bin/env python3
"""Run B08 E3 reference-patch experiments in a disposable Linux copy.

This verifies a known reference patch, not an implemented MDFixer service.
Only Python's standard library, GCC, GNU Make and Git are required.
"""
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
E3 = CASE.parents[1]
ROOT = E3.parent
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
    parser.add_argument("--operator", required=True, help="Actual executor; do not claim manual execution for an AI run")
    parser.add_argument("--output", type=Path, help="New evidence directory; existing directories are rejected")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Run in Linux/Ubuntu WSL, not Windows Python or MinGW.")
    if not args.operator.strip():
        parser.error("--operator must not be blank")
    started = dt.datetime.now(TZ)
    output = (args.output or CASE / "evidence/macro" / started.strftime("%Y%m%dT%H%M%S%f+0800")).resolve()
    if not any(base.resolve() in output.parents for base in (CASE / "evidence", CASE / ".runs")):
        parser.error("Evidence must be a new subdirectory under this case's evidence or .runs.")
    output.mkdir(parents=True, exist_ok=False)
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    files = sorted(p for p in FIXTURE.rglob("*") if p.is_file() and not {"build", "bin"}.intersection(p.relative_to(FIXTURE).parts))
    source_hashes = {p.relative_to(FIXTURE).as_posix(): digest(p) for p in files}
    transcript = output / "commands.txt"
    record = {
        "schema_version": "e3-mdfixer-evidence-v1", "started_at": started.isoformat(),
        "operator": args.operator, "provenance": "REAL_LINUX_REFERENCE_PATCH_EXPERIMENT",
        "review_status": "PENDING_HUMAN_REVIEW", "subject": oracle["subject"],
        "not_a_detector_report": True, "not_an_mdfixer_output": True,
        "declaration_style": "MACRO",
        "status": "RUNNING", "commands": [], "assertions": [], "edits": [], "stages": {},
        "source_sha256": source_hashes, "runner_sha256": digest(Path(__file__)),
        "oracle_sha256": digest(ORACLE), "reference_patch_sha256": digest(PATCH),
        "invalid_patch_sha256": digest(INVALID_PATCH),
        "platform": platform.platform(), "architecture": platform.machine(),
    }
    # Use the Linux toolchain only; do not dump inherited shell variables via make -p.
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}

    def log(text: str) -> None:
        with transcript.open("a", encoding="utf-8") as stream:
            stream.write(text)

    def run(argv, cwd: Path, label: str, allow_failure=False):
        result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env, text=True,
                                encoding="utf-8", errors="replace", capture_output=True, timeout=120)
        record["commands"].append({"label": label, "argv": [str(x) for x in argv], "cwd": str(cwd),
                                   "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        log(f"\n[{label}]\n$ cd {shlex.quote(str(cwd))}\n$ {shlex.join([str(x) for x in argv])}\n"
            f"{result.stdout}{result.stderr}\nexit_code={result.returncode}\n")
        if result.returncode and not allow_failure:
            raise RuntimeError(f"{label}: command failed with exit code {result.returncode}")
        return result

    def check(name: str, condition: bool) -> None:
        record["assertions"].append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    def expected(name: str, value) -> None:
        check(name, value == oracle["expected_behavior"][name])

    def stage(work: Path, name: str, build=None):
        version = run(["./bin/demo", "--version"], work, name + ":version").stdout.strip()
        check(name + ":version is demo 1.0.0", version == "demo 1.0.0")
        behavior = run(["./bin/demo"], work, name + ":behavior").stdout.strip()
        snapshot = {"version_output": version, "behavior_output": int(behavior),
                    "makefile": (work / "Makefile").read_text(encoding="utf-8"),
                    "config_header": (work / "include/config.h").read_text(encoding="utf-8"),
                    "files": {name: {"sha256": digest(work / name), "mtime_ns": (work / name).stat().st_mtime_ns}
                              for name in ["build/main.o", "bin/demo"]}}
        if build is not None:
            snapshot["build_stdout"] = build.stdout
        record["stages"][name] = snapshot
        return snapshot

    def edit_value(work: Path, old: int, new: int) -> None:
        obj = work / "build/main.o"
        time.sleep(max(0, obj.stat().st_mtime + 1.1 - time.time()))
        header = work / "include/config.h"
        text = header.read_text(encoding="utf-8")
        check(f"edit CONFIG_VALUE {old} exists", text.count(f"#define CONFIG_VALUE {old}\n") == 1)
        header.write_text(text.replace(f"#define CONFIG_VALUE {old}\n", f"#define CONFIG_VALUE {new}\n"), encoding="utf-8")
        check(f"CONFIG_VALUE {new} timestamp newer than object", header.stat().st_mtime_ns > obj.stat().st_mtime_ns)
        record["edits"].append({"file": "include/config.h", "old": old, "new": new})
        log(f"EDIT include/config.h: CONFIG_VALUE {old} -> {new}\n")

    try:
        for name in ["gcc", "make", "git", "python3"]:
            if not shutil.which(name):
                raise RuntimeError(f"Required tool missing: {name}")
        record["workspace_commit"] = run(["git", "rev-parse", "HEAD"], ROOT, "workspace commit").stdout.strip()
        record["workspace_status_before"] = run(["git", "status", "--short"], ROOT, "workspace status").stdout
        for relative, sha in source_hashes.items():
            committed = subprocess.run(["git", "show", oracle["subject"]["commit"] + ":" + oracle["subject"]["working_directory"] + "/" + relative],
                                       cwd=ROOT, capture_output=True, timeout=30)
            check("fixture matches fixed commit: " + relative,
                  committed.returncode == 0 and hashlib.sha256(committed.stdout).hexdigest() == sha)
        record["environment"] = {name: run([name, "--version"], ROOT, name + " version").stdout for name in ["gcc", "make", "git", "python3"]}
        record["environment"]["os_release"] = Path("/etc/os-release").read_text(encoding="utf-8")
        config_basis = {"architecture": platform.machine(), "os_release": record["environment"]["os_release"],
                        "gcc": record["environment"]["gcc"].splitlines()[0],
                        "make": record["environment"]["make"].splitlines()[0],
                        "cppflags": "-Iinclude", "cflags": "-Wall -Wextra -O2", "build_mode": "GNU Make release"}
        record["configuration_basis"] = config_basis
        record["configuration_id"] = "b08-macro-" + hashlib.sha256(json.dumps(config_basis, sort_keys=True).encode()).hexdigest()[:16]
        record["configuration_note"] = "Measured toolchain/options identifier; commit and image identity are recorded separately. No Docker image used."
        check("oracle declares Macro style", oracle["declaration_style"] == "MACRO")
        check("fixed input is MD-only", len(oracle["findings"]) == 1 and oracle["findings"][0]["type"] == "MISSING")
        (output / "input").mkdir()
        shutil.copy2(ORACLE, output / "input/md-report.json")
        shutil.copy2(FIXTURE / "Makefile", output / "input/Makefile.before")
        shutil.copy2(PATCH, output / "input/reference.patch")
        shutil.copy2(INVALID_PATCH, output / "input/invalid.patch")
        with tempfile.TemporaryDirectory(prefix="b08-e3-mdfixer-") as temporary:
            work = Path(temporary) / "sample"
            shutil.copytree(FIXTURE, work, ignore=shutil.ignore_patterns("build", "bin"))
            record["temporary_workdir"] = str(work)
            run(["make", "clean"], work, "before:clean")
            initial = stage(work, "initial", run(["make", "-j2"], work, "before:build"))
            expected("initial", initial["behavior_output"])
            dependencies = run(["gcc", "-MM", "-Iinclude", "-MT", "build/main.o", "src/main.c"], work, "actual project-header dependencies").stdout
            record["compiler_dependencies"] = dependencies
            actual_files = set(dependencies.replace("\\\n", " ").split(":", 1)[1].split())
            check("compiler reads both project headers", actual_files == {"src/main.c", "include/common.h", "include/config.h"})
            declarations = run(["make", "-np", "build/main.o"], work, "before:Make database").stdout
            target_before = next(line for line in declarations.splitlines() if line.startswith("build/main.o:"))
            record["declared_target_before"] = target_before
            check("Make omits config.h and declares common.h", set(target_before.split()[1:]) == {"src/main.c", "include/common.h"})
            before_makefile = (work / "Makefile").read_bytes()
            source_rule = next(line for line in before_makefile.decode().splitlines() if line.startswith("build/main.o:"))
            check("Macro target prerequisites are only DEPS", source_rule == "build/main.o: $(DEPS)")
            edit_value(work, 4, 5)
            stale = stage(work, "before_fix_config_4_to_5_incremental", run(["make", "-j2"], work, "before:header-only incremental"))
            expected("before_fix_config_4_to_5_incremental", stale["behavior_output"])
            check("missing dependency leaves object and executable unchanged", stale["files"] == initial["files"])
            run(["make", "clean"], work, "before:clean comparison")
            clean = stage(work, "before_fix_config_4_to_5_clean", run(["make", "-j2"], work, "before:clean comparison build"))
            expected("before_fix_config_4_to_5_clean", clean["behavior_output"])
            edit_value(work, 5, 4)
            run(["git", "apply", "--check", PATCH], work, "reference:patch check")
            run(["git", "apply", PATCH], work, "reference:patch apply")
            fixed_makefile = (work / "Makefile").read_bytes()
            (output / "input/Makefile.reference").write_bytes(fixed_makefile)
            run(["make", "clean"], work, "reference:clean")
            fixed = stage(work, "after_fix_config_4_clean", run(["make", "-j2"], work, "reference:build"))
            expected("after_fix_config_4_clean", fixed["behavior_output"])
            declarations = run(["make", "-np", "build/main.o"], work, "reference:Make database").stdout
            target_after = next(line for line in declarations.splitlines() if line.startswith("build/main.o:"))
            record["declared_target_after"] = target_after
            check("reference declarations equal GCC project dependencies", set(target_after.split()[1:]) == actual_files)
            check("reference changes only DEPS", fixed_makefile == before_makefile.replace(
                b"DEPS := src/main.c include/common.h\n",
                b"DEPS := src/main.c include/common.h include/config.h\n"))
            check("reference preserves pure Macro style", "build/main.o: $(DEPS)" in fixed_makefile.decode().splitlines())
            edit_value(work, 4, 5)
            updated = stage(work, "after_fix_config_4_to_5_incremental", run(["make", "-j2"], work, "reference:first header-only incremental"))
            expected("after_fix_config_4_to_5_incremental", updated["behavior_output"])
            check("first repaired header edit recompiles", "-c src/main.c -o build/main.o" in updated["build_stdout"] and updated["files"]["build/main.o"] != fixed["files"]["build/main.o"])
            edit_value(work, 5, 6)
            updated_again = stage(work, "after_fix_config_5_to_6_incremental", run(["make", "-j2"], work, "reference:second header-only incremental"))
            expected("after_fix_config_5_to_6_incremental", updated_again["behavior_output"])
            check("second repaired header edit recompiles", "-c src/main.c -o build/main.o" in updated_again["build_stdout"] and updated_again["files"]["build/main.o"] != updated["files"]["build/main.o"])
            noop = stage(work, "after_fix_noop", run(["make", "-j2"], work, "reference:no-op incremental"))
            expected("after_fix_noop", noop["behavior_output"])
            check("no-op does not rebuild products", noop["files"] == updated_again["files"])
            record["reference_decision"] = {"decision": "ACCEPTED", "method": "REFERENCE_PATCH_EXPERIMENT_NOT_MDFIXER_SERVICE", "build": "PASSED", "incremental_function": "PASSED", "md_recheck": "PASSED", "rd_remaining": False}
            try:
                run(["git", "apply", "--check", INVALID_PATCH], work, "invalid:patch check")
                run(["git", "apply", INVALID_PATCH], work, "invalid:patch apply")
                (output / "input/Makefile.invalid").write_bytes((work / "Makefile").read_bytes())
                candidate = run(["make", "-B", "-j2"], work, "invalid:forced build", allow_failure=True)
                expected("invalid_candidate_build_exit_nonzero", candidate.returncode != 0)
                check("candidate fails at deliberate false command", "false" in candidate.stdout and "Error" in candidate.stderr)
                record["invalid_candidate"] = {"decision": "REJECTED", "build_exit_code": candidate.returncode,
                                                "reason": "Candidate inserts false before compilation; validation failed.",
                                                "restored_to": "last accepted reference Makefile"}
            finally:
                (work / "Makefile").write_bytes(fixed_makefile)
                log("RESTORE Makefile: last accepted reference bytes\n")
                record["invalid_candidate_makefile_restored"] = (work / "Makefile").read_bytes() == fixed_makefile
            check("rollback restores exact accepted Makefile", record["invalid_candidate_makefile_restored"])
            run(["make", "clean"], work, "rollback:clean")
            restored = stage(work, "restored_output", run(["make", "-j2"], work, "rollback:build"))
            expected("restored_output", restored["behavior_output"])
            record["invalid_candidate"]["restoration"] = "PASSED"
        check("repository fixture unchanged", all(digest(FIXTURE / p) == sha for p, sha in source_hashes.items()))
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
        rows = "\n".join(f"| {name} | {snapshot['behavior_output']} |" for name, snapshot in record["stages"].items())
        (output / "README.md").write_text(
            f"# MDFixer MACRO 实际运行记录\n\n"
            f"- 执行时间：{started.isoformat()}。\n- 实际执行者：{args.operator}。\n"
            f"- 固定样例提交：`{oracle['subject']['commit']}`。\n"
            f"- 运行时仓库提交：`{record.get('workspace_commit', '未取得')}`。\n"
            f"- 配置标识：`{record.get('configuration_id', '未取得')}`。\n"
            f"- 结果：**{record['status']}**，{passed}/{len(record['assertions'])} 项断言通过。\n"
            f"- 人工审阅：待实际 B08 成员确认。\n\n"
            f"| 实验阶段 | 实际输出 |\n|---|---|\n{rows}\n\n"
            f"原始命令、标准输出、错误输出与退出码见 commands.txt；完整元数据、目标文件哈希及时间戳见 observations.json。\n\n"
            f"此记录验证已知参考补丁及候选拒绝恢复流程，不是 MDFixer 自动修复输出或 BuildChecker 检测报告。此 Macro 案例只验证 DEPS 中 config.h 的 MD 修复，不含刻意加入的项目内 RD。\n\n"
            f"{('失败原因：' + record['error']) if 'error' in record else '修复后两次只改头文件均自动重建；故意失败候选被拒绝，恢复后完整构建与功能检查通过。'}\n",
            encoding="utf-8")
    print(f"{record['status']}\nASSERTIONS={passed}/{len(record['assertions'])}\nEVIDENCE_DIR={output}")
    if record["status"] != "PASS":
        print(record.get("error", "See observations.json"))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
