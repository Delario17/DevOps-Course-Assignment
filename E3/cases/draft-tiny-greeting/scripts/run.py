#!/usr/bin/env python3
"""Verify the B08 E3 DRAFT baseline and preserve reproducible evidence."""
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


CASE = Path(__file__).resolve().parents[1]
E3 = CASE.parents[1]
ROOT = E3.parent
FIXTURE = CASE / "fixture"
ORACLE = CASE / "oracle/expected.json"
TZ = dt.timezone(dt.timedelta(hours=8))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True, help="Actual person or automation that starts this run")
    parser.add_argument("--output", type=Path, help="New evidence directory; existing directories are rejected")
    parser.add_argument(
        "--docker",
        choices=("auto", "required", "skip"),
        default="auto",
        help="auto records PARTIAL when Docker is unavailable; required fails; skip records an intentional skip",
    )
    args = parser.parse_args()

    started = dt.datetime.now(TZ)
    output = (
        args.output
        or CASE / "evidence" / started.strftime("%Y%m%dT%H%M%S%f+0800")
    ).resolve()
    if output == ROOT or output == E3 or output == FIXTURE or FIXTURE in output.parents:
        parser.error("Evidence must not be inside the source fixture.")
    output.mkdir(parents=True, exist_ok=False)
    (output / "input").mkdir()

    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    fixture_files = sorted(
        path for path in FIXTURE.rglob("*") if path.is_file() and path.name != "hello"
    )
    source_hashes = {
        path.relative_to(FIXTURE).as_posix(): digest(path) for path in fixture_files
    }
    transcript = output / "commands.txt"
    record: dict[str, object] = {
        "schema_version": "e3-draft-evidence-v1",
        "started_at": started.isoformat(),
        "operator": args.operator,
        "provenance": "REAL_LOCAL_AND_OPTIONAL_DOCKER_BASELINE_EXPERIMENT",
        "review_status": "PENDING_HUMAN_REVIEW",
        "subject": oracle["subject"],
        "status": "RUNNING",
        "commands": [],
        "assertions": [],
        "source_sha256": source_hashes,
        "runner_sha256": digest(Path(__file__)),
        "oracle_sha256": digest(ORACLE),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "docker_mode": args.docker,
    }
    env = {
        "PATH": os.defpath,
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": tempfile.gettempdir(),
    }

    def log(text: str) -> None:
        with transcript.open("a", encoding="utf-8") as stream:
            stream.write(text)

    def run(
        argv: list[str | Path],
        cwd: Path,
        label: str,
        *,
        allow_failure: bool = False,
        timeout: int = 300,
        command_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [str(item) for item in argv]
        result = subprocess.run(
            command,
            cwd=cwd,
            env=command_env or env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
        entry = {
            "label": label,
            "argv": command,
            "cwd": str(cwd),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        commands = record["commands"]
        assert isinstance(commands, list)
        commands.append(entry)
        log(
            f"\n[{label}]\n$ cd {shlex.quote(str(cwd))}\n$ {shlex.join(command)}\n"
            f"{result.stdout}{result.stderr}\nexit_code={result.returncode}\n"
        )
        if result.returncode and not allow_failure:
            raise RuntimeError(f"{label}: command failed with exit code {result.returncode}")
        return result

    def check(name: str, condition: bool) -> None:
        assertions = record["assertions"]
        assert isinstance(assertions, list)
        assertions.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    try:
        for executable in ("git", "make", "cc"):
            if not shutil.which(executable, path=env["PATH"]):
                raise RuntimeError(f"Required native tool missing: {executable}")

        record["workspace_commit"] = run(
            ["git", "rev-parse", "HEAD"], ROOT, "workspace commit"
        ).stdout.strip()
        record["workspace_status_before"] = run(
            ["git", "status", "--short"], ROOT, "workspace status"
        ).stdout

        fixed_commit = oracle["subject"]["commit"]
        fixed_commit_fixture = oracle["subject"]["fixed_commit_working_directory"]
        for relative, sha256 in source_hashes.items():
            committed = subprocess.run(
                [
                    "git",
                    "show",
                    f"{fixed_commit}:{fixed_commit_fixture}/{relative}",
                ],
                cwd=ROOT,
                capture_output=True,
                timeout=30,
            )
            check(
                "fixture matches fixed commit: " + relative,
                committed.returncode == 0
                and hashlib.sha256(committed.stdout).hexdigest() == sha256,
            )

        tool_versions = {
            "git": run(["git", "--version"], ROOT, "git version").stdout.strip(),
            "make": run(["make", "--version"], ROOT, "make version").stdout.splitlines()[0],
            "cc": run(["cc", "--version"], ROOT, "cc version").stdout.splitlines()[0],
            "python": sys.version.splitlines()[0],
        }
        record["environment"] = tool_versions
        configuration_basis = {
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "make": tool_versions["make"],
            "cc": tool_versions["cc"],
            "base_image": oracle["project"]["base_image"],
        }
        record["configuration_basis"] = configuration_basis
        record["configuration_id"] = "b08-draft-" + hashlib.sha256(
            json.dumps(configuration_basis, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]

        for path in fixture_files:
            destination = output / "input" / path.relative_to(FIXTURE)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        shutil.copy2(ORACLE, output / "input/oracle.json")

        with tempfile.TemporaryDirectory(prefix="b08-e3-draft-") as temporary:
            work = Path(temporary) / "sample"
            shutil.copytree(FIXTURE, work, ignore=shutil.ignore_patterns("hello"))
            record["temporary_workdir"] = str(work)

            run(["make", "clean"], work, "native:clean")
            build = run(["make"], work, "native:build")
            hello = work / "hello"
            check("native build emits compiler command", "main.c -o hello" in build.stdout)
            check("native executable exists", hello.is_file() and os.access(hello, os.X_OK))
            behavior = run(["./hello"], work, "native:behavior")
            check(
                "native behavior output",
                behavior.returncode == oracle["expected_behavior"]["program_exit_code"]
                and behavior.stdout.strip() == oracle["expected_behavior"]["program_stdout"],
            )
            version = run(["./hello", "--version"], work, "native:version")
            check(
                "native version output",
                version.stdout.strip() == oracle["expected_behavior"]["version_stdout"],
            )
            test_result = run(["make", "test"], work, "native:functional test")
            check(
                "native functional test",
                test_result.returncode
                == oracle["expected_behavior"]["functional_test_exit_code"],
            )
            native_result = {
                "decision": "PASSED",
                "build_exit_code": build.returncode,
                "program_exit_code": behavior.returncode,
                "program_stdout": behavior.stdout.strip(),
                "version_stdout": version.stdout.strip(),
                "functional_test_exit_code": test_result.returncode,
                "executable_sha256": digest(hello),
            }
            record["native_validation"] = native_result
            write_json(output / "native-validation.json", native_result)

        broken_text = (FIXTURE / "Dockerfile.broken").read_text(encoding="utf-8")
        reference_text = (FIXTURE / "Dockerfile.reference").read_text(encoding="utf-8")
        check("both Dockerfiles share BASE_IMAGE argument", "ARG BASE_IMAGE=" in broken_text and "ARG BASE_IMAGE=" in reference_text)
        check("broken Dockerfile invokes make", "RUN make" in broken_text)
        check("broken Dockerfile omits package installation", "apt-get" not in broken_text)
        check("reference Dockerfile installs gcc make libc6-dev", all(name in reference_text for name in ("gcc", "make", "libc6-dev")))
        check("reference Dockerfile builds the project", "RUN make" in reference_text)
        check("both images run hello", 'CMD ["./hello"]' in broken_text and 'CMD ["./hello"]' in reference_text)

        docker_search_path = os.environ.get("PATH", os.defpath)
        docker_path = shutil.which("docker", path=docker_search_path)
        if args.docker == "skip":
            docker_result = {
                "decision": "SKIPPED_BY_REQUEST",
                "reason": "The operator selected --docker skip.",
            }
            record["docker_validation"] = docker_result
            record["status"] = "PARTIAL"
        elif not docker_path:
            docker_result = {
                "decision": "UNAVAILABLE",
                "reason": "docker executable is not available on PATH",
                "next_command": "python3 E3/cases/draft-tiny-greeting/scripts/run.py --operator <name> --docker required",
            }
            record["docker_validation"] = docker_result
            if args.docker == "required":
                raise RuntimeError(docker_result["reason"])
            record["status"] = "PARTIAL"
        else:
            docker_env = dict(env)
            docker_env["PATH"] = docker_search_path
            for name in ("HOME", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG", "XDG_RUNTIME_DIR"):
                if value := os.environ.get(name):
                    docker_env[name] = value
            run([docker_path, "version"], ROOT, "docker:version", command_env=docker_env)
            run([docker_path, "info"], ROOT, "docker:daemon info", command_env=docker_env)
            base_tag = oracle["project"]["base_image"]
            run([docker_path, "pull", base_tag], ROOT, "docker:pull base", timeout=900, command_env=docker_env)
            base_inspect = run(
                [docker_path, "image", "inspect", base_tag],
                ROOT,
                "docker:inspect base",
                command_env=docker_env,
            )
            base_metadata = json.loads(base_inspect.stdout)[0]
            repo_digests = base_metadata.get("RepoDigests") or []
            check("base image has a resolved repo digest", bool(repo_digests))
            resolved_base = repo_digests[0]
            stamp = started.strftime("%Y%m%d%H%M%S")
            broken_tag = f"b08-e3-draft-broken:{stamp}"
            reference_tag = f"b08-e3-draft-reference:{stamp}"

            broken_build = run(
                [
                    docker_path,
                    "build",
                    "--no-cache",
                    "--build-arg",
                    f"BASE_IMAGE={resolved_base}",
                    "-f",
                    "Dockerfile.broken",
                    "-t",
                    broken_tag,
                    ".",
                ],
                FIXTURE,
                "docker:broken build",
                allow_failure=True,
                timeout=900,
                command_env=docker_env,
            )
            broken_log = broken_build.stdout + broken_build.stderr
            check("broken image build exits nonzero", broken_build.returncode != 0)
            check(
                "broken image identifies missing make",
                oracle["expected_behavior"]["broken_image_failure_signature"] in broken_log,
            )

            reference_build = run(
                [
                    docker_path,
                    "build",
                    "--no-cache",
                    "--build-arg",
                    f"BASE_IMAGE={resolved_base}",
                    "-f",
                    "Dockerfile.reference",
                    "-t",
                    reference_tag,
                    ".",
                ],
                FIXTURE,
                "docker:reference build",
                timeout=1200,
                command_env=docker_env,
            )
            check("reference image build succeeds", reference_build.returncode == 0)
            image_inspect = run(
                [docker_path, "image", "inspect", reference_tag],
                ROOT,
                "docker:inspect reference",
                command_env=docker_env,
            )
            image_metadata = json.loads(image_inspect.stdout)[0]
            container = run(
                [docker_path, "run", "--rm", reference_tag],
                ROOT,
                "docker:reference behavior",
                command_env=docker_env,
            )
            check(
                "reference container output",
                container.returncode
                == oracle["expected_behavior"]["reference_container_exit_code"]
                and container.stdout.strip()
                == oracle["expected_behavior"]["reference_container_stdout"],
            )
            container_version = run(
                [docker_path, "run", "--rm", reference_tag, "./hello", "--version"],
                ROOT,
                "docker:reference version",
                command_env=docker_env,
            )
            check(
                "reference container version",
                container_version.stdout.strip() == oracle["expected_behavior"]["version_stdout"],
            )
            docker_result = {
                "decision": "PASSED",
                "base_image_tag": base_tag,
                "base_image_id": base_metadata.get("Id"),
                "base_image_repo_digest": resolved_base,
                "broken_image_tag": broken_tag,
                "broken_build_exit_code": broken_build.returncode,
                "broken_failure_signature": oracle["expected_behavior"]["broken_image_failure_signature"],
                "reference_image_tag": reference_tag,
                "reference_image_id": image_metadata.get("Id"),
                "reference_container_exit_code": container.returncode,
                "reference_container_stdout": container.stdout.strip(),
                "reference_container_version": container_version.stdout.strip(),
            }
            record["docker_validation"] = docker_result
            record["status"] = "PASS"

        write_json(output / "docker-validation.json", record["docker_validation"])
    except Exception as error:
        record["status"] = "FAIL"
        record["error"] = f"{type(error).__name__}: {error}"
    finally:
        record["finished_at"] = dt.datetime.now(TZ).isoformat()
        assertions = record["assertions"]
        commands = record["commands"]
        assert isinstance(assertions, list)
        assert isinstance(commands, list)
        passed = sum(bool(item["passed"]) for item in assertions)
        write_json(output / "observations.json", record)
        status = record["status"]
        docker_decision = (record.get("docker_validation") or {}).get("decision", "NOT_RUN")
        next_step = (
            "容器验证已完成，失败环境与参考环境均符合 Oracle。"
            if status == "PASS"
            else "在 Docker 可用的 Linux 或 Docker Desktop 环境运行：`python3 E3/cases/draft-tiny-greeting/scripts/run.py --operator \"姓名\" --docker required`。"
        )
        (output / "README.md").write_text(
            "# DRAFT Tiny Greeting 实际运行记录\n\n"
            f"- 执行时间：{started.isoformat()}。\n"
            f"- 实际执行者：{args.operator}。\n"
            f"- 固定样例提交：`{oracle['subject']['commit']}`。\n"
            f"- 运行时仓库提交：`{record.get('workspace_commit', '未取得')}`。\n"
            f"- 配置标识：`{record.get('configuration_id', '未取得')}`。\n"
            f"- 总体状态：**{status}**。\n"
            f"- 本机构建与功能验证：`{(record.get('native_validation') or {}).get('decision', 'NOT_RUN')}`。\n"
            f"- Docker 验证：`{docker_decision}`。\n"
            f"- 断言：{passed}/{len(assertions)} 通过；记录命令：{len(commands)} 条。\n"
            "- 人工审阅：待实际 B08 成员确认。\n\n"
            "完整元数据见 `observations.json`，原始命令、标准输出、错误输出和退出码见 `commands.txt`。\n\n"
            f"{next_step}\n",
            encoding="utf-8",
        )

    print(
        f"{record['status']}\nASSERTIONS={passed}/{len(assertions)}\n"
        f"COMMANDS={len(commands)}\nEVIDENCE_DIR={output}"
    )
    if record["status"] == "PASS":
        return 0
    if record["status"] == "PARTIAL":
        return 2
    print(record.get("error", "See observations.json"))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
