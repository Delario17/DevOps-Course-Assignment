# B08 E6 实验报告：两轮自动构建与同一镜像的程序验证

## 1. 实验信息与目标

| 项目 | 记录 |
|---|---|
| 姓名 / 学号 | 朱雨乐 / 241250011 |
| 小组 / 轨道 | B08 / B，DRAFT |
| 实验日期 | 2026-11-03 |
| 仓库 | https://github.com/Delario17/DevOps-Course-Assignment |
| 个人分支 | `student/241250011/e6` |
| 服务器工作目录 | `/root/241250011/B08-remote-repo/E6` |
| 首次运行源码 SHA | `3e88ed6efd11c11b42ecaa675fa6ec8ff93a17aa` |
| 新增测试后最终运行源码 SHA | `2b4585d29a94495d4419b4d2af2d0d9912783576` |
| 首次运行目录 | `work/e6-zyl-20261103-190714` |
| 修改后服务构建及测试目录 | `work/build-e6-zyl-final-20261103-190714` |
| 最终运行目录 | `work/e6-zyl-final-20261103-210714` |

E5 已完成候选生成、选择和手工复建。本次 E6 复用本人选定的 `error-02`，由服务自动完成初始构建、失败分类、候选构建和程序验证，并保存能够关联输入、候选、镜像和输出的结构化证据。随后新增一项候选约束测试，重建服务镜像并重新执行 E6，检查修改后的版本是否仍满足原始样例预期。

首次和最终两次运行均通过保存证据的一致性校验。修改后的服务测试为 `26 passed in 0.17s`，个人定向测试退出码为 `0`，最终两轮工作流整体退出码为 `0`。

## 2. 输入来源与实验设置

### 2.1 本人 E5 候选

本次复用的候选由本人在 E5 中通过 DeepSeek 网页交互取得，模型版本按来源记录为 `DeepSeek V4.1 Flash`，生成日期为 2026-11-01。E5 候选选择及原始提示、回复索引见 `E5/docs/zyl-e5-b.md`。E6 不重新调用模型 API。

| 项目 | 记录 |
|---|---|
| 候选编号 | `error-02` |
| E5 源码 SHA | `a1d731a2418c7f545e2c0600083d3220b9f2d3bb` |
| E5 原候选 | `E5/work/e5-zyl-20261101-103032/candidates/error-02/Dockerfile` |
| E6 输入副本 | `E6/inputs/zyl-error-02/Dockerfile` |
| 来源材料 | `E6/inputs/zyl-error-02/README.md`、`e5-provenance.json` |
| 候选 SHA256 | `92d1cb0b766427c2d598a0641f03b2e04bc702bfb3e9d7bda4541fd88b17d92c` |

首次和最终运行的 `invocation.json` 均记录 `replay=false`、`candidate_source="student supplied; see student provenance record"`，候选哈希与 E5 保持一致。核心结果中的 `DRAFT_TEACHING_REPLAY` 和 `Manual model response replay` 表示执行已保存候选的机制，不表示本次重新生成候选，也不改变该候选来自本人 E5 网页交互的事实。

最终候选内容为：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN make
CMD ["./hello"]
```

### 2.2 初始项目与镜像地址

项目为 Tiny Greeting，输入包含 `main.c`、`Makefile` 和 README 等文件，构建命令为 `make`，程序验证命令为 `./hello`，预期输出为 `hello E3`。

本组新版 E6 已将初始样例的镜像地址统一为 `m.daocloud.io/docker.io/library/python:3.13-slim`，候选使用同一地址及固定 digest。该镜像地址适配和 `test_e6_mirror_candidate.py` 属于已有组内参考版本，本人复用它们，不将其计为本人新增实现。

候选校验后生成的第一轮输入使用同一固定 digest，但没有依赖安装步骤，因此仍需真实重现缺少 `make` 的失败。第二轮使用保存的完整候选增加构建依赖。

### 2.3 执行方式

所有实验从本人服务器仓库的 `E6/` 执行。`scripts/course.py` 读取局部 Git 学号，选择个人服务镜像 `course1027-draft:241250011`，再调用 `scripts/lab_cloud.py`。服务挂载候选和证据目录，通过宿主机 Docker 执行构建；最终被测程序使用第二轮镜像 ID，在禁网和资源受限条件下运行。

本次设置单次构建预算为 7200 秒。它是构建上限，不是实际运行耗时。新的输出目录保留每次执行结果，不覆盖先前证据。

## 3. 首次 E6 自动工作流

首次入口启动时间为 `2026-11-03T11:09:04.964611+00:00`，即中国标准时间 19:09:04.964611。输出目录名 `190714` 是此前设置变量时取得的编号，不作为精确启动时间。

对应操作为：

```bash
python3 scripts/course.py e6 \
  --candidate inputs/zyl-error-02/Dockerfile \
  --out work/e6-zyl-20261103-190714 \
  --build-timeout 7200
```

首次 `result.json` 和校验输出记录：

| 项目 | 实际结果 |
|---|---|
| trace_id | `e6-b-9bfde719b2bd4471831e7028265fdbe1` |
| 第一轮构建 | 退出 `1`，`failure_class=MISSING_MAKE` |
| 第二轮构建 | 退出 `0` |
| 第二轮镜像 ID | `sha256:010f8eb94a629daf45e98e36cb3489d813211e12b4c24b341a4fc22d43598bf4` |
| 程序验证 | 退出 `0`，输出 `hello E3\n`，`output_matches=true` |
| 工作流状态 | `SUCCEEDED` |
| elapsed_ms | `1198`，即核心工作流约 1.198 秒 |
| 证据一致性校验 | `passed=true` |

第一轮命令使用 `/evidence/iter-01/Dockerfile`，第二轮使用 `/evidence/iter-02/Dockerfile`，构建上下文均为 `/evidence/project`。首次验证命令最后一个参数与第二轮的 `image_id` 相同，说明运行对象与构建产物对应。

这里的 `/evidence` 是服务容器路径，对应服务器本次运行目录中的 `evidence/`。

## 4. 核心代码机制与结果对应

核心文件为 `services/draft/draft/autobuild.py`。

### 4.1 instructions：合并逻辑指令

`instructions` 按行读取 Dockerfile，跳过空行和整行注释，合并反斜杠续行及连续空白，得到逻辑指令列表。本人候选中的依赖安装跨两行书写，先被合并成一条逻辑 `RUN` 指令，再参与候选比较。

该函数采用教学样例的文本解析规则，不等于实现完整 Dockerfile 语法解析。

### 4.2 prepare_candidate：约束候选并生成第一轮输入

`prepare_candidate` 检查候选非空、第一条 FROM 使用固定 digest、只有一个构建阶段、初始与候选基础镜像地址一致，以及项目、构建和启动指令按顺序保留。候选允许额外增加修复用的 RUN 指令。

函数返回的是固定镜像后的初始输入，不是修复后的候选。它用候选固定的 FROM 替换初始文件第一行，保留初始文件其他指令，不加入候选中的依赖安装。因此两轮使用同一基础镜像，第一轮仍处于缺 make 的状态，第二轮才使用完整修复候选。

### 4.3 classify_failure：确认初始失败类型

`classify_failure` 检查构建日志中的缺 make 特征，返回 `MISSING_MAKE`；部分镜像解析或连接错误归为 `INFRASTRUCTURE`；其余归为 `OTHER_BUILD_ERROR`。

本次第一轮退出 `1`，分类为 `MISSING_MAKE`。工作流要求构建确实失败且分类符合预期，才继续第二轮。单独出现非零退出码不足以证明复现成功，网络故障也不能替代目标失败。

### 4.4 execute：统一执行命令及保存日志

`execute` 使用 `subprocess.Popen` 启动命令，分别写入标准输出和标准错误文件，通过 `wait(timeout=...)` 等待并返回退出码。超过预算时终止客户端进程组并抛出超时异常。

本次两轮构建、镜像检查和程序验证均由该函数执行。成功运行证明这些命令在本次输入下完成；本次没有实际触发超时，不能以此声称超时故障场景已经验收。

### 4.5 auto_build：串联构建与同镜像验证

`auto_build` 检查输入和输出目录，保存项目副本与输入哈希，按顺序执行初始输入和候选两轮构建。第一轮重现缺 make 后进入第二轮；第二轮失败则停止程序验证。

第二轮成功后，函数通过 `docker image inspect` 读取镜像 ID，将其写入 attempt，再把同一 ID 作为 `docker run` 的实际参数。验证同时检查程序退出码和输出文本，去除输出末尾换行后与 `hello E3` 比较。两项均满足才设置 `SUCCEEDED`。

程序在结束阶段尝试清理验证容器并保存 `result.json`。本报告没有额外提供容器清理日志，因而不对未展示的清理响应作具体判断。

## 5. 本人新增测试

本人新增文件：

```text
E6/services/draft/tests/test_student_241250011_e6.py
```

测试目的为：当一个候选增加第二条 FROM、变成多阶段构建时，应在执行 Docker 构建前被拒绝。测试代码为：

```python
import pytest

from draft.autobuild import prepare_candidate


def test_zyl_rejects_multiple_from_in_candidate():
    base = (
        "FROM python:3.13-slim\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )

    pinned = "FROM python:3.13-slim@sha256:" + "a" * 64

    candidate = base.replace(
        "FROM python:3.13-slim", pinned
    ).replace(
        "RUN make\n",
        "RUN apt-get update && apt-get install -y build-essential\n"
        "RUN make\n",
    )

    candidate += "\nFROM ubuntu:24.04\n"

    with pytest.raises(
        ValueError,
        match="Only single-stage candidates are supported",
    ):
        prepare_candidate(base, candidate)
```

测试先构造具有合法固定 digest 和项目指令的候选，再增加第二条 FROM，断言抛出指定 `ValueError`。其中重复字符 digest 是单测合成输入，只用于字符串约束检查，不下载镜像。

已有参考测试覆盖基础镜像改变、缺少固定 digest、绕过构建和替换启动命令等情况；本人新增测试专门覆盖多个构建阶段的拒绝分支。测试示例来自本次助手交流指导，本人将其加入个人分支、重建镜像，并完成定向与完整服务测试。它验证候选校验函数的行为，不是一个额外的真实 Docker 故障构建实验。

## 6. 修改后重建与测试结果

修改代码和测试后重新构建服务镜像，使新增文件进入镜像。构建及测试记录保存在：

```text
work/build-e6-zyl-final-20261103-190714
```

完整服务测试的 `unit-tests/exit-code.json` 为：

```json
{"exit_code": 0}
```

`unit-tests/stdout.log` 为：

```text
..........................                                               [100%]
26 passed in 0.17s
```

个人定向测试命令为：

```bash
docker run --rm --network none \
  course1027-draft:241250011 \
  pytest tests/test_student_241250011_e6.py -q
```

`student-test.log` 显示：

```text
.                                                                        [100%]
```

`student-test-exit-code.txt` 为 `0`。服务测试与个人定向测试均通过。参考版本含 25 项测试定义，本人新增一项后，本次实际完整运行数量为 26 项。

## 7. 修改后最终 E6 重跑

新增测试后重新执行原始工作流，使用新的输出目录，保留首次结果：

```bash
python3 scripts/course.py e6 \
  --candidate inputs/zyl-error-02/Dockerfile \
  --out work/e6-zyl-final-20261103-210714 \
  --build-timeout 7200
```

最终 `source-commit.txt` 记录源码 SHA 为 `2b4585d29a94495d4419b4d2af2d0d9912783576`，终端显示个人分支为 `student/241250011/e6`，`git status --short` 没有列出未提交修改。

`invocation.json` 记录启动时间 `2026-11-03T13:07:14.397299+00:00`，即中国标准时间 21:07:14.397299，服务镜像仍为 `course1027-draft:241250011`，候选来源为 student supplied，哈希与 E5 一致。

| 项目 | 首次运行 | 新增测试后最终运行 |
|---|---|---|
| trace_id | `e6-b-9bfde719b2bd4471831e7028265fdbe1` | `e6-b-23abb8ad561b4ee68e6bff0ba49ab29b` |
| 第一轮分类 | `MISSING_MAKE` | `MISSING_MAKE` |
| 第二轮构建退出码 | `0` | `0` |
| 程序退出码 | `0` | `0` |
| 标准输出 | `hello E3\n` | `hello E3\n` |
| output_matches | `true` | `true` |
| 核心工作流计时 | 1198 ms | 2549 ms |
| 保存证据校验 | `passed=true` | `passed=true` |

最终入口退出码为 `0`。最终第二轮镜像及验证命令使用同一 ID：

```text
sha256:f5f6becb393b72c41212fbb336588668369dd20ba944e08738846aba0abd191a
```

最终验证命令使用 `--network none --cpus 1 --memory 128m --pids-limit 64`，末尾参数为上述镜像 ID。输出为 `hello E3\n`、退出码为 `0`、`output_matches=true`，表明修改后的服务版本仍满足本样例预期。

两次计时均来自 `auto_build` 的核心工作流，不含此前服务镜像构建及 pytest。是否命中缓存应通过两轮构建日志判断，本报告不将 1.198 秒或 2.549 秒解释为首次依赖安装或无缓存构建耗时。

## 8. 最终证据一致性校验

执行：

```bash
python3 scripts/verify_e6_b_evidence.py \
  --run-dir work/e6-zyl-final-20261103-210714/evidence \
  > work/e6-zyl-final-20261103-210714/evidence-check.json
```

校验入口退出码为 `0`，输出为：

```json
{
  "passed": true,
  "trace_id": "e6-b-23abb8ad561b4ee68e6bff0ba49ab29b",
  "baseline_failure": "MISSING_MAKE",
  "fixed_build_exit_code": 0,
  "verify_exit_code": 0,
  "verified_output": "hello E3",
  "candidate_sha256": "92d1cb0b766427c2d598a0641f03b2e04bc702bfb3e9d7bda4541fd88b17d92c",
  "image_id": "sha256:f5f6becb393b72c41212fbb336588668369dd20ba944e08738846aba0abd191a",
  "scope": "Saved evidence consistency; does not independently rerun builds"
}
```

校验脚本检查两轮顺序、初始缺 make 的日志、候选及项目文件哈希、镜像 ID 和程序输出的对应关系。它核对保存的证据，不独立重新执行构建。真实运行结论与完整服务测试结果分别由工作流记录、构建日志及 pytest 日志支撑。

## 9. 本人贡献及实验范围

本人复用本人 E5 的选定候选及来源，使用组内独立 E6 参考版本完成两轮自动构建和证据校验，阅读并解释核心实现，新增多阶段候选拒绝测试，并在重建后完成 26 项服务测试、个人定向测试和最终 E6 重跑。个人实验版本与结果分别保存，报告使用运行时 SHA，不用后续写报告的提交替代它。

核心工作流和镜像地址回归测试来自组内已有实现；本人本次新增的是 `test_student_241250011_e6.py`，没有将已有算法或他人测试写为本人新增成果。报告整理、操作命令和测试示例使用助手辅助。

本实验只覆盖 Tiny Greeting 教学样例以及已保存候选的自动构建验证，没有证明完整论文项目集合上的成功率、多轮自主模型修复或跨服务集成。模型在 E5 网页交互阶段使用，本次 E6 没有调用模型 API。E7 的完整故障矩阵和 CI 门禁不列为本次已完成内容。

## 10. 证据索引与交付

以下路径均相对于服务器 `/root/241250011/B08-remote-repo/E6`。

| 路径 | 内容 |
|---|---|
| `inputs/zyl-error-02/Dockerfile` | 本人选定的 E5 候选副本 |
| `inputs/zyl-error-02/README.md`、`e5-provenance.json` | 输入来源及原 E5 来源记录 |
| `services/draft/tests/test_student_241250011_e6.py` | 本人新增候选约束测试 |
| `work/e6-zyl-20261103-190714/source-commit.txt` | 首次运行源码 SHA |
| `work/e6-zyl-20261103-190714/invocation.json` | 首次入口时间、服务标签和候选来源 |
| `work/e6-zyl-20261103-190714/evidence/result.json` | 首次两轮构建和验证结果 |
| `work/e6-zyl-20261103-190714/evidence-check.json` | 首次证据校验 |
| `work/build-e6-zyl-final-20261103-190714/unit-tests/` | 26 项服务测试的 stdout、stderr 和退出码 |
| `work/build-e6-zyl-final-20261103-190714/student-test.log`、`student-test-exit-code.txt` | 个人定向测试及退出码 |
| `work/e6-zyl-final-20261103-210714/source-commit.txt` | 最终运行源码 SHA |
| `work/e6-zyl-final-20261103-210714/workflow-exit-code.txt` | 最终入口退出码 |
| `work/e6-zyl-final-20261103-210714/invocation.json` | 最终入口时间、服务标签和候选哈希 |
| `work/e6-zyl-final-20261103-210714/runner/` | 服务启动命令、输出与退出码 |
| `work/e6-zyl-final-20261103-210714/evidence/project/` | 实际项目副本及输入文件 |
| `work/e6-zyl-final-20261103-210714/evidence/iter-01/` | 第一轮 Dockerfile 和完整构建日志 |
| `work/e6-zyl-final-20261103-210714/evidence/iter-02/` | 第二轮候选、构建日志和 image-inspect.json |
| `work/e6-zyl-final-20261103-210714/evidence/result.json` | 最终两轮执行及程序验证报告 |
| `work/e6-zyl-final-20261103-210714/evidence/verify.log`、`verify-stderr.log` | 程序标准输出及错误输出 |
| `work/e6-zyl-final-20261103-210714/evidence-check.json` | 最终证据一致性校验 |
| `docs/zyl-e6-验收记录.csv` | 个人验收记录 |

源码、个人测试、输入来源、报告及验收记录通过个人分支 PR 提交。完整 work 保留在本人服务器目录并单独归档下载，不加入 Git。
