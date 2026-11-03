# E6 B组：两轮构建与程序验证

## 1. 基本信息及作业范围

- 姓名：盛浩宇；学号：241250008；小组：B08。
- 实验日期：2026-11-03T17:48:26+08:00（北京时间）。
- 仓库：https://github.com/Delario17/DevOps-Course-Assignment
- 上游main版本：`cc1cac261d38527cd191e21985e2a72d3590b747`。
- 本次被测源码版本：`ab0553085f1bbe2890f7af6b9ff9740dd8351c16`，在上游版本基础上仅增加本人失败测试。
- 运行位置：`/root/241250008/B08-remote-repo/E6`。
- 范围：E6自动两轮构建、同一镜像ID运行验证、证据校验、核心机制解释及一项失败测试。未运行E7完整gate和远程CI。
- 本次由当前Codex对话助手按本人授权在服务器代办，包含测试编写、运行核验和报告整理；不声明本人独立手工执行。

## 2. 同步代码及环境

通过本人电脑获取最新GitHub代码并制作完整Git bundle，在本人服务器克隆中fetch并从最新main创建`student/241250008/e6-validation`。E4、E5的work记录保留；不修改其他学号目录，不清理共享Docker资源。

| 项目 | 实测 |
|---|---|
| 系统 | Ubuntu 22.04.5 LTS |
| 架构 | x86_64 |
| CPU / 可见内存 | 2 / 1.7 GiB |
| Docker Engine | 29.1.3 |
| 自检 | problems=[]，通过；低于建议值的warnings保留 |
| 服务构建 | 退出0 |
| 服务单测 | 26 passed（上游25项，加本人1项） |

本组代码已将最低可见内存门槛设置为1.5 GiB，本次未修改配置。

## 3. 输入和候选来源

项目输入为`fixtures/draft/`，功能是编译并运行`./hello`，预期精确输出`hello E3`。本次复用本人E5保存并真实验证过的候选，复制至`work/candidate-241250008/Dockerfile`，并保留原来源记录。没有冒用仓库`inputs/error-03`中其他同学的候选来源。

- E5原候选：`../E5/work/candidates-241250008/error-01/Dockerfile`。
- 本次候选SHA256：`cc9e790c86259c95ff55819042c0f143a465e212b5dd6ee91dd868ad87627cae`。
- 来源：E5当前助手生成的方案；其初始方案与包内参考内容一致，随后为解决官方源停滞改用清华Debian源并添加下载参数，详情保留在E5报告和来源文件。
- 本次E6没有生成新模型回复，也没有调用模型API；属于对已保存候选的自动执行验证。
- 与组级README中的默认候选不同，本次明确用`--candidate`传入本人候选。

最终输入候选：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN sed -i \
    -e 's|https\?://deb.debian.org/debian-security|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g' \
    -e 's|https\?://security.debian.org/debian-security|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g' \
    -e 's|https\?://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g' \
    /etc/apt/sources.list.d/debian.sources
RUN apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30 update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN make
CMD ["./hello"]
```

## 4. 实际命令

以下命令从个人仓库的E6目录执行，先补充第7节测试，再构建包含测试和最新服务代码的镜像。

```bash
python3 scripts/doctor.py --out work/doctor-241250008-20261103/env.json
python3 scripts/course.py build --out work/build-241250008-20261103 --build-timeout 1200
docker run --rm --network none course1027-draft:241250008 pytest tests/test_student_241250008_multistage.py -q
python3 scripts/course.py e6 --candidate work/candidate-241250008/Dockerfile --out work/e6-241250008-20261103-02 --build-timeout 1200
python3 scripts/verify_e6_b_evidence.py --run-dir work/e6-241250008-20261103-02/evidence
```

每个阶段在全新work子目录保存证据。运行时日志重定向到`work/e6-241250008-20261103-meta/`，退出码在对应txt文件中记录。

## 5. 两轮执行及程序验证结果

| 阶段 | 实测 | 解释 |
|---|---|---|
| 候选校验 | 通过 | 保留固定FROM和项目、编译、运行指令 |
| 第一轮 | build_exit_code=1，MISSING_MAKE | 在相同基础镜像环境真实到达RUN make，不把网络错误当目标失败 |
| 第二轮 | build_exit_code=0 | 使用保存候选补齐编译工具并构建成功 |
| 程序运行 | exit_code=0 | 对第二轮镜像ID执行docker run |
| 标准输出 | `hello E3`加换行 | output_matches=true |
| 工作流终态 | SUCCEEDED | runner保存的退出码为0 |

首轮`work/e6-241250008-20261103`得到SUCCEEDED且证据校验通过，但SSH断线导致外层退出码文件缺失，未补写或伪造。故另在全新`work/e6-241250008-20261103-02`运行，并用服务器后台包装脚本独立保存进程退出码。本文结果来自第二次完整运行：E6进程退出0、runner退出0、证据校验退出0；首轮记录同时保留，不混用两轮的镜像ID。

第一轮错误原始行，位于`evidence/iter-01/build-stderr.log`：

```text
29: #8 0.166 /bin/sh: 1: make: not found
33: 0.166 /bin/sh: 1: make: not found
```

第二轮构建镜像ID：`sha256:b57132f11d0372450e4654ab6afcc7ac8943564cdf391f80ad0e1f144de2f698`。

该ID同时出现在`result.json`的`attempts[1].image_id`、`verification.command`最后一个参数和`iter-02/image-inspect.json`的`Id`中；程序使用禁网运行，不用镜像标签代替这项一致性核对。

## 6. 保存证据的校验

校验脚本退出0，结果如下：

```json
{
  "passed": true,
  "trace_id": "e6-b-3e6c7b9c7f6a414585031c652958fec8",
  "baseline_failure": "MISSING_MAKE",
  "fixed_build_exit_code": 0,
  "verify_exit_code": 0,
  "verified_output": "hello E3",
  "candidate_sha256": "cc9e790c86259c95ff55819042c0f143a465e212b5dd6ee91dd868ad87627cae",
  "image_id": "sha256:b57132f11d0372450e4654ab6afcc7ac8943564cdf391f80ad0e1f144de2f698",
  "scope": "Saved evidence consistency; does not independently rerun builds"
}
```

脚本核对两轮编号、初始缺make日志、候选SHA256、镜像inspect与运行ID、退出码与输出，以及保存项目输入的哈希。此脚本验证已有文件的一致性，不会独立重跑构建；真实两轮执行由前一步完成。

## 7. 个人失败测试与价值

新增文件：`services/draft/tests/test_student_241250008_multistage.py`。

上游测试已覆盖修改基础镜像、绕过make、伪造输出、构建失败和超时等。本项进一步验证多阶段候选在进入Docker执行前被拒绝，且不创建半成品证据目录。使用monkeypatch使任何Docker命令调用直接导致测试失败，避免仅检查错误消息而遗漏副作用。

```python
"""Student 241250008: reject multi-stage candidates before any Docker call."""
import pytest
from draft import autobuild


def test_multistage_rejected_before_docker_or_evidence(tmp_path, monkeypatch):
    fixture = tmp_path / 'fixture'
    fixture.mkdir()
    base = ('FROM python:3.13-slim\nWORKDIR /work\n'
            'COPY main.c Makefile ./\nRUN make\nCMD ["./hello"]\n')
    (fixture / 'Dockerfile.broken').write_text(base)
    pinned = 'FROM python:3.13-slim@sha256:' + 'a' * 64
    candidate_text = base.replace('FROM python:3.13-slim', pinned).replace(
        'RUN make\n', 'RUN apt-get update && apt-get install -y build-essential\nRUN make\n')
    candidate_text += 'FROM scratch\n'
    candidate = tmp_path / 'candidate.Dockerfile'
    candidate.write_text(candidate_text)
    output = tmp_path / 'evidence'

    def forbidden_execute(*args, **kwargs):
        pytest.fail('Invalid multi-stage input must not start any Docker command')

    monkeypatch.setattr(autobuild, 'execute', forbidden_execute)
    with pytest.raises(ValueError, match='Only single-stage candidates are supported'):
        autobuild.auto_build(fixture, candidate, output, 'hello E3')
    assert not output.exists(), 'Rejected input must not leave partial evidence'
```

定向结果：`1 passed`，退出0。加入测试后重新构建服务，完整服务结果为`26 passed`，退出0。该项是确定性单元测试，不是一次真实多阶段Docker构建；正常两轮真实构建另有第5节证据。

测试代码保存在本次被测源码commit及完整备份中，代码全文在本报告给出以便复现。按本人此前要求，待提交分支仅包含本报告，不提交work或额外源码文件；测试源码commit不随本次报告PR推送。

## 8. 核心机制解释

1. `instructions`合并反斜杠续行，去除空行和注释，形成规范逻辑指令。
2. `prepare_candidate`检查固定digest、单阶段、相同镜像tag，并要求按顺序保留原始项目指令。候选增加RUN安装依赖，初始轮只固定相同FROM而不提前加入修复。
3. `classify_failure`识别真实shell的make缺失；基础设施和其他编译错误不算复现成功，因此第一轮必须到达MISSING_MAKE才能继续。
4. `execute`保存命令输出和退出码，并在超时时终止客户端进程组。
5. `auto_build`先构建初始输入，再构建候选；inspect第二轮结果获得image_id，以该ID运行程序，分别检查退出码和输出，保存result.json及清理记录。

上述范围是课程两轮工作流，不包含自动在线生成候选，也不代表论文完整数据集或修复成功率评测。

## 9. 证据索引与备份

以下路径相对个人服务器E6目录，均不作为GitHub附件提交：

| 内容 | 路径 |
|---|---|
| 环境 | `work/doctor-241250008-20261103/env.json` |
| 服务镜像构建、inspect、26项测试 | `work/build-241250008-20261103/` |
| 源码版本、定向测试、退出码、校验输出 | `work/e6-241250008-20261103-meta/` |
| 候选及E5来源 | `work/candidate-241250008/` |
| 两轮Dockerfile与构建日志 | `work/e6-241250008-20261103-02/evidence/iter-01/`、`iter-02/` |
| 镜像ID、运行命令、功能结果 | 同次`evidence/result.json`、`iter-02/image-inspect.json`、`verify.log` |
| 入口命令与外层退出码 | 同次`runner/command.json`、`runner/exit-code.json` |

完整记录另行打包下载本人电脑。GitHub提交仅包含`E6/docs/shy-e6-b.md`，保留其他同学文件原样。
