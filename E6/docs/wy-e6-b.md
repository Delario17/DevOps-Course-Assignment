# B08 E6 实验报告：两轮自动构建与同一镜像的程序验证

## 1. 实验信息与目标

| 项目 | 记录 |
|---|---|
| 姓名 / 学号 | 王祎 / 241250007 |
| 小组 / 轨道 | B08 / B，DRAFT |
| 实验日期 | 2026 年 11 月 3 日 |
| 入口启动时间 | 中国标准时间 14:36:27.615501；`invocation.json` 保存 UTC 时间 `2026-11-03T06:36:27.615501+00:00` |
| 仓库 | https://github.com/Delario17/DevOps-Course-Assignment |
| 实验源码 SHA | `18c59b5efa2c3e83a64b6e73d66ed912536b10da` |
| 源码提交说明 | `E6: add isolated B workflow and mirror regression test` |
| 服务器工作目录 | `/root/241250007/DevOps-Course-Assignment/E6` |
| 服务器证据目录 | `/root/241250007/DevOps-Course-Assignment/E6/work/e6-01` |
| 服务镜像标签 | `course1027-draft:241250007` |
| 工作流标识 | `e6-b-282d3ea0383b4905b878f56571faa578` |
| 单次构建预算 | 7200 秒，来自 `runner/command.json` 的 `--timeout` |

E5 已完成候选生成、选择和手工复建。E6 将选定候选接入自动工作流：先在固定镜像下重现缺少 `make` 的初始失败，再使用候选完成第二轮构建，并按第二轮镜像 ID 运行程序。实验关注输入、错误反馈、构建产物与程序结果之间的对应关系，使一次修复能够通过保存的原始文件逐项核验。

本次整体退出码为 `0`，工作流终态为 `SUCCEEDED`。第一轮构建退出 `1`，分类为 `MISSING_MAKE`；第二轮构建退出 `0`；功能验证输出 `hello E3`、退出 `0`；保存证据的一致性校验结果为 `passed=true`。

## 2. 输入来源与实验环境

### 2.1 目录和执行分工

本组保留分阶段目录，E6 服务代码、实验入口、输入、报告和运行证据均位于 `E6/`。Mac 负责 GitHub 操作和报告整理，云服务器负责 Docker 实验。E5 的原始记录保留在原目录中。

实际服务启动命令记录了以下设置：

| 设置 | 实际值 |
|---|---|
| 服务容器 | `course1027-draft:241250007` |
| 服务执行身份 | `--user 0:0` |
| 服务网络 | `--network bridge` |
| Docker 连接 | 挂载 `/var/run/docker.sock:/var/run/docker.sock` |
| 附加组 | `--group-add 120` |
| 候选挂载 | 宿主机 `E6/inputs/error-03/Dockerfile` 只读挂载到 `/inputs/Dockerfile` |
| 证据挂载 | 宿主机 `E6/work/e6-01/evidence` 挂载到 `/evidence` |
| 被测镜像平台 | `linux/amd64`，来自 `iter-02/image-inspect.json` |

服务容器中的 Docker 客户端通过宿主机引擎完成两轮构建。报告中的 `/evidence/...` 是服务容器路径，对应服务器的 `E6/work/e6-01/evidence/...`。

### 2.2 复用 E5 的选定候选

本次通过 `--candidate inputs/error-03/Dockerfile` 使用本人 E5 的 `error-03`。候选由 DeepSeek 网页交互生成，具体模型版本在 E5 中记为“未记录”，选择过程见 `E5/docs/wy-e5-b.md`。

| 项目 | 记录 |
|---|---|
| E5 源码 SHA | `2e76b52466b87b50523343b43cda9da5b743b4ac` |
| E5 原候选 | `/root/241250007/DevOps-Course-Assignment/E5/work/e5-02/candidates/error-03/Dockerfile` |
| E6 输入副本 | `inputs/error-03/Dockerfile` |
| 来源说明 | `inputs/error-03/README.md` |
| 候选 SHA-256 | `71edb07d22ab10726e3aec89d1611cf31306f756054d8edb8101179ee99f11ce` |

`invocation.json` 记录 `replay=false` 和 `candidate_source="student supplied; see student provenance record"`，对应显式传入本人候选的路线。核心报告中的 `DRAFT_TEACHING_REPLAY` 和 `Manual model response replay` 描述的是执行已保存候选的机制，本次 E6 运行没有调用模型 API。

核对 `inputs/error-03/Dockerfile` 与本次 `evidence/iter-02/Dockerfile`，二者字节内容一致，哈希与 E5 记录相同。

### 2.3 项目和基础镜像

Tiny Greeting 的 `main.c` 调用 `puts("hello E3")`，Makefile 使用 `cc main.c -o hello` 编译。程序验收条件为执行 `./hello`，输出 `hello E3` 并退出 `0`。

本次固定基础镜像为：

```text
m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
```

E6 中将 `fixtures/draft/Dockerfile.broken` 的镜像地址统一为 `m.daocloud.io/docker.io/library/python:3.13-slim`。`prepare_candidate` 先检查原始地址和候选去掉 digest 后的地址一致，再将候选的固定 digest 用于第一轮初始输入。由此两轮保持相同基础镜像，同时第一轮仍保留缺少构建工具的状态。

## 3. 自动工作流的实现

入口为 `scripts/course.py`，它根据仓库本地学号选择服务镜像，再调用 `scripts/lab_cloud.py`。后者将候选和输出目录挂入服务容器，执行 `python3 -m draft auto-build`。

核心文件是 `services/draft/draft/autobuild.py`，各函数沿一次工作流依次处理：

| 函数 | 在本次实验中的作用 |
|---|---|
| `instructions` | 合并反斜杠续行和连续空白，提取 Dockerfile 逻辑指令 |
| `prepare_candidate` | 检查单阶段、固定 digest、原始镜像地址，以及项目、构建和运行指令的保留情况，生成固定镜像后的初始输入 |
| `execute` | 执行 Docker 命令，将标准输出和错误分别保存，并处理超时 |
| `classify_failure` | 从第一轮日志识别 `MISSING_MAKE`、`INFRASTRUCTURE` 或 `OTHER_BUILD_ERROR` |
| `auto_build` | 保存项目副本和输入哈希，按顺序构建两轮，读取第二轮镜像 ID，运行验证并写入 `result.json` |

第一轮必须实际构建失败且分类为 `MISSING_MAKE`，工作流才进入第二轮。第二轮构建退出 `0` 后，程序通过 `docker image inspect` 取得镜像 ID，再使用该 ID 运行容器。只有程序退出 `0` 且输出匹配，最终状态才更新为 `SUCCEEDED`。

## 4. 本人改动与新增回归测试

本人在独立 `E6/` 中复用教学实现，保存 E5 候选及来源，统一样例的 DaoCloud 镜像地址，并新增：

```text
services/draft/tests/test_e6_mirror_candidate.py
```

测试 `test_mirror_candidate_requires_matching_baseline` 设置两种输入：

| 测试输入 | 预期行为 |
|---|---|
| 初始文件与候选均使用相同 DaoCloud 地址，候选附带 digest | 返回保留原始指令、使用候选 digest 的初始 Dockerfile |
| 初始文件改回 `python:3.13-slim`，候选仍使用 DaoCloud 地址 | 抛出 `ValueError`，错误包含 `Candidate changed the original base image tag` |

该测试将本次镜像站适配涉及的地址一致性要求写成回归检查。测试中的重复字符 digest 用于校验指令处理，不触发镜像下载。

这项测试已包含在记录的实验源码提交中。本次提供的证据目录包含 E6 工作流和校验结果；服务构建及 pytest 的输出属于 `work/build-e6-01/`，未随本次证据一起提供，服务单测执行数量应与该目录中的日志关联填写。

## 5. 执行命令与第一轮失败

在服务器 `E6/` 中运行：

```bash
python3 scripts/course.py e6 \
  --candidate inputs/error-03/Dockerfile \
  --out work/e6-01 \
  --build-timeout 7200

E6_CODE=$?
printf '%s\n' "$E6_CODE" > work/e6-01/workflow-exit-code.txt
git rev-parse HEAD > work/e6-01/source-commit.txt
```

`runner/command.json` 保存服务容器的实际启动参数，`runner/exit-code.json` 和 `workflow-exit-code.txt` 均记录 `0`。`runner/stdout.log` 中的 JSON 与 `evidence/result.json` 内容一致，`runner/stderr.log` 为空。

第一轮实际 Dockerfile 为：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

工作流执行：

```bash
docker build --progress=plain \
  -f /evidence/iter-01/Dockerfile \
  -t e6-draft-replay:282d3ea0383b4905b878f56571faa578-1 \
  /evidence/project
```

`iter-01/build-stderr.log` 保存 43 行输出，其中关键记录为：

```text
#8 [4/4] RUN make
#8 0.340 /bin/sh: 1: make: not found
#8 ERROR: process "/bin/sh -c make" did not complete successfully: exit code: 127
```

shell 内部命令退出 `127`，外层 `docker build` 退出 `1`。`result.json` 的第一条 attempt 记录 `failure_class="MISSING_MAKE"`，满足进入候选轮的条件。

## 6. 第二轮构建与缓存情况

第二轮使用保存的 `error-03`：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN apt-get update && apt-get install -y --no-install-recommends make gcc libc6-dev && rm -rf /var/lib/apt/lists/*
RUN make
CMD ["./hello"]
```

相对第一轮，候选仅增加构建依赖安装和 apt 索引清理。项目源码、工作目录、编译入口和启动命令保持一致。

第二轮实际命令为：

```bash
docker build --progress=plain \
  -f /evidence/iter-02/Dockerfile \
  -t e6-draft-replay:282d3ea0383b4905b878f56571faa578-2 \
  /evidence/project
```

`iter-02/build-stderr.log` 同样保存 43 行输出，依赖安装与编译步骤均命中缓存：

```text
#8 [4/5] RUN apt-get update && apt-get install -y --no-install-recommends make gcc libc6-dev && rm -rf /var/lib/apt/lists/*
#8 CACHED

#9 [5/5] RUN make
#9 CACHED
```

第二轮构建退出 `0`，导出镜像的日志显示 `#10 DONE 0.1s`。整个核心工作流的 `elapsed_ms` 为 `1977`，即 1.977 秒，计时覆盖两轮构建、镜像检查、运行和清理。该次运行复用了宿主机已有镜像层，首次依赖下载的耗时见 E5 的构建日志。

镜像检查记录的 `Created` 为 `2026-10-31T16:16:09.717238151+08:00`，与本次 11 月 3 日命中既有构建缓存的情况一致。第二轮使用本次工作流的独立标签保存产物，后续验证按检查得到的镜像 ID 执行。

## 7. 同一镜像 ID 的功能验证

`iter-02/image-inspect.json`、第二轮 attempt 和验证命令中的镜像标识一致：

```text
sha256:b40b1613f7784b18ed0246092c5ff57379c2750e9731dd496b59918273684fc0
```

镜像配置记录工作目录为 `/work`，默认命令为 `["./hello"]`，平台为 `linux/amd64`。报告保存的实际验证命令为：

```bash
docker run --rm \
  --network none \
  --cpus 1 \
  --memory 128m \
  --pids-limit 64 \
  --cidfile /evidence/verify-container-id.txt \
  sha256:b40b1613f7784b18ed0246092c5ff57379c2750e9731dd496b59918273684fc0
```

本次自动验证使用 128 MiB 内存限制。构建服务使用 bridge 网络，最终被测程序使用禁网环境，验证执行的是第二轮产物的默认程序。

| 检查项 | 实际结果 |
|---|---|
| 第一轮构建 | 退出 `1`，`MISSING_MAKE` |
| 第二轮构建 | 退出 `0` |
| 验证标准输出 | `hello E3\n` |
| 验证标准错误 | 空 |
| 验证退出码 | `0` |
| `output_matches` | `true` |
| 工作流状态 | `SUCCEEDED` |
| 工作流及服务调用退出码 | 均为 `0` |

验证容器记录在 `verify-container-id.txt`，命令带有 `--rm`。工作流最后额外调用 `docker rm -f` 时，`cleanup-stderr.log` 返回该 ID 对应的 `No such container`，符合容器运行结束后已自动删除的情况。该清理响应与程序验证结果分别保存。

## 8. 保存证据的一致性校验

在服务器执行：

```bash
python3 scripts/verify_e6_b_evidence.py \
  --run-dir work/e6-01/evidence \
  > work/e6-01/evidence-check.json
```

`evidence-check.json` 记录：

```json
{
  "passed": true,
  "trace_id": "e6-b-282d3ea0383b4905b878f56571faa578",
  "baseline_failure": "MISSING_MAKE",
  "fixed_build_exit_code": 0,
  "verify_exit_code": 0,
  "verified_output": "hello E3",
  "candidate_sha256": "71edb07d22ab10726e3aec89d1611cf31306f756054d8edb8101179ee99f11ce",
  "image_id": "sha256:b40b1613f7784b18ed0246092c5ff57379c2750e9731dd496b59918273684fc0",
  "scope": "Saved evidence consistency; does not independently rerun builds"
}
```

撰写报告时，对保存证据重新运行同一校验脚本，结果仍为 `passed=true`。校验覆盖：

- 两轮 attempt 的数量和顺序，以及第一轮缺少 `make` 的实际日志。
- 第二轮退出码、保存候选的 SHA-256 与报告对应关系。
- `image-inspect.json`、第二轮 attempt、运行命令三处镜像 ID 的一致性。
- 输出文件、报告中的实际输出和 `hello E3` 预期的一致性。
- `project/` 中各输入文件的 SHA-256，以及构建上下文中参考答案文件的排除情况。

该校验针对已保存文件的相互对应关系；两轮 Docker 执行和程序输出分别由原始日志与命令记录支撑。

## 9. 本次结果与 E5 的衔接

E5 通过网页获取候选并手工复建，E6 将同一候选纳入服务的两轮自动执行。候选 SHA-256 保持一致，变化集中在执行方式：由服务生成初始输入、识别目标失败、构建修复候选、检查镜像并调用程序验证。

本次结果显示，工作流先捕获 `make: not found`，随后使用修复候选得到可运行镜像，并将实际运行对象绑定到第二轮镜像 ID。输入哈希、候选哈希、两轮日志和验证命令共同构成可核对的记录。新增镜像地址回归测试对应了本组使用 DaoCloud 时的候选校验要求。

## 10. 服务器证据索引

以下路径均相对于服务器目录：

```text
/root/241250007/DevOps-Course-Assignment/E6/work/e6-01
```

| 相对路径 | 内容 |
|---|---|
| `source-commit.txt` | 实验源码 SHA |
| `workflow-exit-code.txt` | 入口整体退出码 `0` |
| `invocation.json` | 阶段、时间、镜像标签、候选来源与哈希 |
| `runner/command.json` | 实际服务容器命令、挂载、身份和超时参数 |
| `runner/stdout.log`、`stderr.log`、`exit-code.json` | 服务返回报告、错误输出与退出码 |
| `service-container-id.txt` | 服务容器 ID |
| `evidence/project/` | 实际项目副本及初始模板 |
| `evidence/iter-01/Dockerfile` | 固定 digest 后的第一轮初始输入 |
| `evidence/iter-01/build-stdout.log`、`build-stderr.log` | 第一轮完整构建输出 |
| `evidence/iter-02/Dockerfile` | 本次选定修复候选 |
| `evidence/iter-02/build-stdout.log`、`build-stderr.log` | 第二轮完整构建输出及缓存记录 |
| `evidence/iter-02/image-inspect.json`、`inspect-stderr.log` | 第二轮镜像详情与检查错误输出 |
| `evidence/verify.log`、`verify-stderr.log` | 程序标准输出与标准错误 |
| `evidence/verify-container-id.txt` | 验证容器 ID |
| `evidence/cleanup.log`、`cleanup-stderr.log` | 验证容器清理记录 |
| `evidence/result.json` | 状态、两轮命令、退出码、输入哈希、镜像 ID 和验证结果 |
| `evidence-check.json` | 保存证据的一致性校验结果 |

源码中的候选与来源说明位于 `E6/inputs/error-03/`，新增测试位于 `E6/services/draft/tests/test_e6_mirror_candidate.py`。E5 原始候选生成和选择记录继续对应 `E5/work/e5-02/`，报告见 `E5/docs/wy-e5-b.md`。
