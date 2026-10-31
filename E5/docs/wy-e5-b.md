# B08 E5 实验报告：失败反馈驱动的 Dockerfile 修复与手工复建

## 1. 实验信息与目标

| 项目 | 记录 |
|---|---|
| 姓名 / 学号 | 王祎 / 241250007 |
| 小组 / 轨道 | B08 / B，DRAFT |
| 实验日期 | 2026 年 10 月 31 日 |
| 初始证据采集时间 | 2026-10-31 11:17:51，中国标准时间；`invocation.json` 保存 UTC 时间 `2026-10-31T03:17:51.984968+00:00` |
| 仓库 | https://github.com/Delario17/DevOps-Course-Assignment |
| 实验源码 SHA | `2e76b52466b87b50523343b43cda9da5b743b4ac` |
| 服务器实际工作目录 | `/root/241250007/DevOps-Course-Assignment/E5` |
| 服务器证据目录 | `/root/241250007/DevOps-Course-Assignment/E5/work/e5-02` |
| 服务镜像标签记录 | `course1027-draft:241250007`，来自 `invocation.json` |
| 候选生成 | DeepSeek 网页交互，两类提示分别生成三个候选；具体模型版本记为“未记录” |
| 最终候选 | `error-03`，自主请求模型生成，`is_recorded_replay=false` |

本次实验围绕一个问题展开：如何利用真实构建失败反馈，为已有 Dockerfile 补齐构建环境，并用实际程序行为验证修复结果。具体做法是固定项目源码和基础镜像，以缺少 `make` 的失败日志生成两类提示，比较六个模型候选，选定其中一个完成真实构建，再运行该镜像验证输出。

## 2. 执行方式与输入

### 2.1 目录及环境设置

本组继续按实验阶段组织仓库。E5 的服务、脚本、项目样例、报告和运行证据均位于 `E5/`。Mac 负责 GitHub 操作、浏览器模型交互和证据备份，云服务器负责 Docker 构建与程序验证。

本组使用标称 2 GiB 的云服务器，E5 自检最低可见内存按组内配置调整为 1.5 GiB。候选构建日志显示容器内软件源为 Debian trixie，下载的软件包架构为 `amd64`。本报告的 E5 证据统一定位到服务器 `/root/241250007/DevOps-Course-Assignment/E5/work/e5-02`，宿主系统版本、Docker 版本、资源自检和基线单测日志另属环境准备记录。

服务构建与 E5 入口采用教师提供的 E5—E7 B 组参考代码；本次执行内容为 E5 失败采集、模型候选比较与手工复建。候选修复通过显式安装依赖完成，选定 Dockerfile 的 `manual_changes` 记录为空。

### 2.2 Tiny Greeting 项目

`project/` 保存本次构建上下文，项目由 `main.c`、`Makefile` 和 `README.md` 等文件组成。程序源码为：

```c
#include <stdio.h>
int main(void) { puts("hello E3"); return 0; }
```

Makefile 的编译规则为：

```makefile
all: hello
hello: main.c
	cc main.c -o hello
```

README 明确要求 C 编译器与 GNU Make。验收条件为容器执行 `./hello`，标准输出为一行 `hello E3`，退出码为 `0`。

### 2.3 固定基础镜像与网络适配

此前直接访问 Docker Hub 时出现连接超时，本次将下载地址调整为 DaoCloud，并保持基础镜像 digest：

```text
m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
```

实验源码提交的说明为 `E5: use DaoCloud for pinned fixture base image`。本报告使用服务器证据目录中重新采集的 `e5-02` 记录；此前网络故障的 `e5-01` 属于另一次运行。

采集入口读取包内候选的第一行来统一初始镜像。因此，本次初始输入以 `iter-01/Dockerfile` 为准，`project/Dockerfile.broken` 则保留了模板原有的 `FROM python:3.13-slim` 写法。

## 3. 初始构建失败与错误定位

在服务器 `E5/` 中执行采集入口：

```bash
python3 scripts/course.py e5 \
  --out work/e5-02 \
  --build-timeout 1200

git rev-parse HEAD > work/e5-02/source-commit.txt
```

实际送入 Docker 的命令保存在 `iter-01/build/command.json`：

```bash
docker build --progress=plain \
  -f /root/241250007/DevOps-Course-Assignment/E5/work/e5-02/iter-01/Dockerfile \
  -t course1020-b-broken:c0f3cbc2 \
  /root/241250007/DevOps-Course-Assignment/E5/work/e5-02/project
```

初始 Dockerfile 为：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

构建已完成基础镜像读取和项目复制，在第 4 行 `RUN make` 失败。合并日志 `iter-01/build-retry.log` 共 95 行，第 81—82 行记录：

```text
#8 0.166 /bin/sh: 1: make: not found
#8 ERROR: process "/bin/sh -c make" did not complete successfully: exit code: 127
```

`iter-01/build/exit-code.json` 和 `iter-01/result-retry.json` 均记录外层 Docker 构建退出码为 `1`。其中 shell 命令退出 `127`，表示在该构建环境中找不到 `make`；Docker 将这一失败汇总为构建退出 `1`。

`iter-01/error-localization.json` 将第 81、85 行提取为根因行，来源标记为 `SCRIPT_FROM_ACTUAL_BUILD_LOG`。脚本随后生成两份模型提示。归档保存了内层 Docker 退出码和生成结果，采集入口自身的退出码未单独保存为文件。

## 4. 两种提示与六个模型候选

### 4.1 提示设置与原始回复

错误驱动提示提供实际初始 Dockerfile 和构建日志最后最多 50 行；上下文驱动提示在相同输入上增加项目 README。两类提示均要求保留固定镜像、项目文件、工作目录、构建命令与程序启动命令，并通过安装必要依赖完成修复。

采集脚本生成的提示原文要求返回一个 Dockerfile。本次网页请求将数量改为三个，实际发送版本保存在 `model/`，脚本原始版本保存在 `iter-01/`。

| 提示类型 | 实际发送提示 | 保存的模型回复 | 候选编号 |
|---|---|---|---|
| 错误驱动 | `model/error/prompt.txt` | `model/error/model-response.txt` | `error-01`、`error-02`、`error-03` |
| 上下文驱动 | `model/context/prompt.txt` | `model/context/model-response.txt` | `context-01`、`context-02`、`context-03` |

六份来源记录均填写提供方为 DeepSeek、日期为 2026-10-31、具体版本为“未记录”，并使用 `is_recorded_replay=false`。每份 Dockerfile 从对应回复中提取，单独保存于 `candidates/<编号>/Dockerfile`。

### 4.2 候选比较

六个候选的 `FROM` 均与实际初始输入一致，均保留 `WORKDIR /work`、`COPY main.c Makefile ./`、`RUN make` 和 `CMD ["./hello"]`。

| 候选 | 显式安装的软件包 | 安装与 COPY 顺序 | 清理 apt 索引 | 其他差异 |
|---|---|---|---|---|
| `error-01` | `build-essential` | COPY 后安装 | 是 | 使用构建工具集合 |
| `error-02` | `make gcc libc6-dev` | COPY 后安装 | 是 | 设置 `DEBIAN_FRONTEND=noninteractive` |
| `error-03` | `make gcc libc6-dev` | COPY 后安装 | 是 | 显式依赖、单行安装指令 |
| `context-01` | `build-essential` | COPY 前安装 | 否 | 安装依赖与项目复制分层 |
| `context-02` | `gcc make libc6-dev` | COPY 前安装 | 否 | 显式依赖、安装位于 COPY 前 |
| `context-03` | `build-essential` | COPY 前安装 | 是 | 续行书写、清理索引 |

两类提示都产生了补齐构建工具的方案。上下文驱动的三个候选均将安装步骤放到 `COPY` 之前；错误驱动的三个候选均保留初始文件的复制顺序，在 `COPY` 后增加安装步骤。两类回复中，`build-essential` 方案和显式依赖方案各出现三次。

### 4.3 R1—R4 选择过程

**R1：核对已尝试候选。** 本次归档保存一次选定候选的构建日志，选择前没有保存其他修复候选的构建记录，六个候选进入比较。初始 Dockerfile 的失败单独作为反馈输入保存。

**R2：比较候选一致性。** 采用“将反斜杠续行合并为空格、去除行首行尾空白、合并连续水平空白，保留指令及参数顺序”的文本规则。核对后得到六份不同的规范化文本，没有重复候选形成多数；按依赖方案统计，两类方案各占三个，本规则未确定唯一候选。

**R3：检查核心依赖及项目指令。** 项目 Makefile 调用 `cc` 编译 C 源码，初始环境同时需要补齐 Make 和 C 构建工具。六个候选都提供相关工具的安装方案，固定镜像和项目构建、运行指令也均保留，继续比较修改内容。

**R4：模型辅助选择。** 将六个候选交由本次助手对话比较，建议选择 `error-03`：显式安装 `make`、`gcc`、`libc6-dev`，保留初始指令顺序，并在同一 `RUN` 中清理 apt 索引。该结论已写入 `error-03/来源记录.json` 的 `selection_reason`。DeepSeek 负责生成候选，助手对话参与最终比较；本归档的 `model/` 保存两类生成回复，选择对话保留于实验交流记录。

最终采用 `error-03`，Dockerfile SHA-256 为：

```text
71edb07d22ab10726e3aec89d1611cf31306f756054d8edb8101179ee99f11ce
```

复核六份 Dockerfile 的 SHA-256，均与来源记录中的文本值一致。选中候选保持模型生成的 Dockerfile 内容。

## 5. 选定候选的手工构建

实际选定的 Dockerfile 为：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN apt-get update && apt-get install -y --no-install-recommends make gcc libc6-dev && rm -rf /var/lib/apt/lists/*
RUN make
CMD ["./hello"]
```

相对于初始输入，它在 `RUN make` 前增加一次依赖安装。`make` 执行 Makefile，GCC 提供 C 编译工具，`libc6-dev` 提供编译该程序所需的 C 库开发文件。

手工构建操作采用以下命令，镜像标签和安装指令均与保存的日志对应：

```bash
CANDIDATE_FILE=work/e5-02/candidates/error-03/Dockerfile
CANDIDATE_IMAGE=course1027-e5-candidate:241250007-e5-02

docker build --progress=plain \
  -f "$CANDIDATE_FILE" \
  -t "$CANDIDATE_IMAGE" \
  work/e5-02/project \
  > work/e5-02/candidate-build.log 2>&1

CANDIDATE_CODE=$?
printf '%s\n' "$CANDIDATE_CODE" \
  > work/e5-02/candidate-build-exit-code.txt
```

`candidate-build.log` 保存 278 行构建输出，显示：

```text
#8 [4/5] RUN apt-get update && apt-get install -y --no-install-recommends make gcc libc6-dev && rm -rf /var/lib/apt/lists/*
...
#8 DONE 2384.5s
#9 [5/5] RUN make
#9 0.220 cc main.c -o hello
#9 DONE 0.3s
```

`candidate-build-exit-code.txt` 为 `0`。安装日志记录的关键版本包括：

| 软件包 | 安装版本 |
|---|---|
| `make` | `4.4.1-2` |
| `gcc` | `4:14.2.0-1` |
| `gcc-14` | `14.2.0-19` |
| `libc6-dev` | `2.41-12+deb13u4` |

依赖安装步骤耗时 2384.5 秒，约 39 分 45 秒；其中 apt 索引下载记录为 10.1 MB、13 分 38 秒，软件包下载记录为 57.6 MB、25 分 59 秒。`RUN make` 步骤耗时 0.3 秒，主要耗时集中在依赖下载与安装。

初始采集入口的 `--build-timeout 1200` 作用于该入口调度的构建；本次候选由独立的 `docker build` 命令手工执行，命令未设置上述超时参数，因而完成了超过 1200 秒的依赖安装过程。

## 6. 镜像标识与程序行为验证

构建日志最后将结果命名为：

```text
course1027-e5-candidate:241250007-e5-02
```

`candidate-image-id.txt` 保存的镜像标识为：

```text
sha256:57a63d2737b2eeeb216819a1ff94871a63bc09f2394b84ad9aa7c460d804a24c
```

该值同时出现在构建日志的最终 manifest list 导出行中。构建日志还分别记录 config 和 manifest 摘要，报告按保存的镜像标识关联本次验证。

功能验证采用本次镜像标识运行，操作为：

```bash
IMAGE_ID=$(cat work/e5-02/candidate-image-id.txt)

docker run --rm \
  --network none \
  --cpus 1 \
  --memory 256m \
  --pids-limit 64 \
  "$IMAGE_ID" \
  > work/e5-02/verify.log \
  2> work/e5-02/verify-stderr.log

VERIFY_CODE=$?
printf '%s\n' "$VERIFY_CODE" > work/e5-02/verify-exit-code.txt
```

归档保存了镜像标识、标准输出、标准错误与退出码，验证命令本身按实验操作过程列于上方。

| 检查项 | 实际结果 |
|---|---|
| 候选镜像构建退出码 | `0` |
| 程序标准输出 | `hello E3`，末尾有换行 |
| 程序标准错误 | 空文件 |
| 程序退出码 | `0` |

修复后的镜像完成了 `cc main.c -o hello` 编译，程序实际输出与 README 规定一致。初始失败、依赖安装、编译成功和运行结果由对应日志串联。

## 7. 实验观察与方法设置

本次复现采用“真实失败反馈生成候选，再以真实构建和运行检验候选”的机制。Dockerfile 的固定输入约束使候选比较集中在构建依赖上，程序输出与退出码共同检验修复结果。

错误驱动提示提供 Dockerfile 与日志，上下文驱动提示进一步提供 README。六个候选在依赖表达、安装位置和索引清理上存在差异；本次选择并构建了 `error-03`，其余五份候选保留为比较材料。该轮观察到增加 README 后三个候选均将依赖安装前置，但两类提示都给出了两种依赖方案。

课堂流程采用 Tiny Greeting 教学样例，输入规模为一个 C 源文件及一个 Makefile。模型交互通过网页完成，候选比较与选定候选复建由操作者手工执行。根因提取使用脚本针对实际日志中的 `make: not found` 定位。E5 初始构建和最终候选构建均通过服务器上的 Docker 客户端直接调用宿主机引擎，前置服务镜像按课程入口单独构建。

基础镜像按 digest 固定，apt 软件包在构建时从 Debian trixie 软件源解析实际版本。本报告通过候选哈希、安装日志、镜像标识和验证结果记录这一轮修复使用的具体输入与产物。

## 8. 证据索引与归档核对

下表路径均相对于服务器证据目录 `/root/241250007/DevOps-Course-Assignment/E5/work/e5-02`。例如，`verify.log` 的完整路径为 `/root/241250007/DevOps-Course-Assignment/E5/work/e5-02/verify.log`。

| 证据路径 | 内容 |
|---|---|
| `source-commit.txt` | 实验源码完整 SHA |
| `invocation.json` | 阶段、采集时间、服务标签与回放标记 |
| `project/` | 本次项目构建上下文 |
| `iter-01/Dockerfile` | 统一 digest 后的实际初始输入 |
| `iter-01/build/command.json` | 实际初始 Docker 构建命令 |
| `iter-01/build/stdout.log`、`stderr.log` | 分别保存的完整初始构建输出 |
| `iter-01/build/exit-code.json`、`result-retry.json` | 初始构建退出码 `1` |
| `iter-01/build-retry.log` | 合并日志，第 81、85 行包含根因 |
| `iter-01/error-localization.json` | 日志关键行与定位来源 |
| `iter-01/prompt-*.txt` | 采集脚本生成的提示 |
| `model/error/`、`model/context/` | 实际发送的两类提示和保存的回复 |
| `candidates/*/Dockerfile` | 六个模型候选 |
| `candidates/*/来源记录.json` | 模型来源、日期、路径和候选哈希 |
| `candidate-build.log` | 选定候选的完整构建日志 |
| `candidate-build-exit-code.txt` | 候选构建退出码 `0` |
| `candidate-image-id.txt` | 最终镜像标识 |
| `verify.log`、`verify-stderr.log` | 程序标准输出与标准错误 |
| `verify-exit-code.txt` | 程序退出码 `0` |

证据核对时，`candidates/error-03/来源记录.json` 的 `selection_reason` 字符串后缺少与下一字段分隔的逗号，JSON 解析在第 11 行报错。选择理由与哈希文本均可读取，Dockerfile 哈希也已独立复核；该来源记录需补齐逗号后再供程序解析。撰写报告时未修改原始证据。

本次 E5 的结果为：固定初始镜像下复现了缺少 `make` 的构建失败，保存两类提示与六个候选，按 R1—R4 选择 `error-03`，候选构建退出 `0`，最终程序输出 `hello E3`、退出 `0`。
