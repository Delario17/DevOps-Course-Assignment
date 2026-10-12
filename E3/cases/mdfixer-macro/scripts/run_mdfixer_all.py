#!/usr/bin/env python3
"""Run available B08 MDFixer reference cases and preserve per-case evidence.

Default: require all four cases. Use --cases available for a partial checkout.
Missing cases and failed runners cannot be reported as a full-suite PASS.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

CASE = Path(__file__).resolve().parents[1]
CASE_ROOT = CASE.parent
E3 = CASE_ROOT.parent
CASES = ("target", "macro", "hybrid", "implicit")
TZ = dt.timezone(dt.timedelta(hours=8))


def case_directory(case):
    if case == "macro":
        return CASE
    return CASE_ROOT / f"mdfixer-{case}"


def required_files(case):
    directory = case_directory(case)
    return [directory / "scripts/run.py", directory / "fixture/Makefile",
            directory / "oracle/expected.json", directory / "patches/reference.patch",
            directory / "patches/invalid.patch"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True, help="Actual executor of this run")
    parser.add_argument("--cases", nargs="+", default=["all"], choices=["all", "available", *CASES])
    parser.add_argument("--output", type=Path, help="New directory under this case's evidence or .runs")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Use Linux/Ubuntu WSL with python3, gcc, make and git.")
    if not args.operator.strip():
        parser.error("--operator must not be blank")
    if any(x in args.cases for x in ("all", "available")) and len(args.cases) != 1:
        parser.error("all/available cannot be combined with other case selections")
    availability = {case: [str(p.relative_to(E3)) for p in required_files(case) if not p.is_file()] for case in CASES}
    selected = list(CASES) if args.cases == ["all"] else (
        [case for case in CASES if not availability[case]] if args.cases == ["available"] else list(dict.fromkeys(args.cases)))
    started = dt.datetime.now(TZ)
    output = (args.output or CASE / "evidence/suite" / started.strftime("%Y%m%dT%H%M%S%f+0800")).resolve()
    allowed = [(CASE / "evidence").resolve(), (CASE / ".runs").resolve()]
    if not any(base in output.parents for base in allowed):
        parser.error("--output must be a new subdirectory under this case's evidence or .runs")
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("Evidence directory already exists; use a new path")
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    summary = {"schema_version": "e3-mdfixer-suite-v1", "started_at": started.isoformat(),
               "operator": args.operator, "requested": args.cases, "selected": selected,
               "not_an_mdfixer_output": True, "review_status": "PENDING_HUMAN_REVIEW",
               "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "case_directories": {case: str(case_directory(case).relative_to(E3)) for case in selected},
               "unavailable": {k: v for k, v in availability.items() if v}, "cases": []}
    failed = not selected
    for case in selected:
        item = {"case": case}
        summary["cases"].append(item)
        if availability[case]:
            item.update(status="MISSING", missing_files=availability[case])
            failed = True
            print(f"{case}: MISSING", flush=True)
            continue
        case_output = output / case
        argv = [sys.executable, str(required_files(case)[0]), "--operator", args.operator,
                "--output", str(case_output)]
        item["argv"] = argv
        try:
            result = subprocess.run(argv, cwd=E3.parent, env=env, text=True, encoding="utf-8",
                                    errors="replace", capture_output=True, timeout=600)
            item["exit_code"] = result.returncode
            (output / f"{case}.runner.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
            observed = json.loads((case_output / "observations.json").read_text(encoding="utf-8"))
            if not isinstance(observed, dict):
                raise ValueError("observations.json must contain an object")
            assertions = observed.get("assertions", [])
            if not isinstance(assertions, list) or not all(isinstance(a, dict) and isinstance(a.get("passed"), bool) for a in assertions):
                raise ValueError("assertions must contain boolean passed fields")
            passed = sum(a.get("passed") is True for a in assertions)
            item.update(assertions_passed=passed, assertions_total=len(assertions), evidence=case,
                        evidence_sha256=hashlib.sha256((case_output / "observations.json").read_bytes()).hexdigest())
            item["status"] = "PASS" if (result.returncode == 0 and observed.get("status") == "PASS"
                                             and assertions and passed == len(assertions)) else "FAIL"
        except subprocess.TimeoutExpired as error:
            def decoded(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
            (output / f"{case}.runner.txt").write_text(decoded(error.stdout) + decoded(error.stderr), encoding="utf-8")
            item.update(status="FAIL", error=f"TimeoutExpired: {error}")
        except (OSError, ValueError) as error:
            item.update(status="FAIL", error=f"{type(error).__name__}: {error}")
        failed = failed or item["status"] != "PASS"
        print(f"{case}: {item['status']} ({item.get('assertions_passed', 0)}/{item.get('assertions_total', 0)})", flush=True)
    summary["status"] = "FAIL" if failed else ("PASS" if set(selected) == set(CASES) else "PASS_SELECTED")
    summary["finished_at"] = dt.datetime.now(TZ).isoformat()
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = "\n".join(f"| {r['case']} | {r['status']} | {r.get('assertions_passed', 0)}/{r.get('assertions_total', 0)} |" for r in summary["cases"])
    (output / "README.md").write_text(
        f"# MDFixer 统一验证记录\n\n执行者：{args.operator}。时间：{started.isoformat()}。\n\n"
        f"结果：**{summary['status']}**。范围为所选案例；四类完成状态由 `--cases all` 的结果记录。\n\n"
        f"| 案例 | 结果 | 断言 |\n|---|---|---|\n{rows}\n\n"
        "各案例子目录保存 Oracle、Patch、命令、输出和恢复证据；summary.json 记录缺失案例和证据哈希。\n"
        "本入口验证已知参考补丁，人工审阅待确认。\n", encoding="utf-8")
    print(f"{summary['status']}\nEVIDENCE_DIR={output}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
