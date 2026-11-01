# B08 E5 实验报告：失败反馈驱动的 Dockerfile 修复与手工复建

## 1. 实验信息与目标

| 项目 | 记录 |
|---|---|
| 姓名 / 学号 | 朱雨乐 / 241250011 |
| 小组 / 轨道 | B08 / B，DRAFT |
| 实验日期 | 2026-11-01 |
| 仓库 | https://github.com/Delario17/DevOps-Course-Assignment |
| 实验源码 SHA | `a1d731a2418c7f545e2c0600083d3220b9f2d3bb` |
| 服务器工作目录 | `/root/241250011/B08-remote-repo/E5` |
| 本次证据目录 | `work/e5-zyl-20261101-103032`，相对于上述工作目录 |
| 初始采集时间 | `2026-11-01T02:31:09.462359+00:00`，即中国标准时间 2026-11-01 10:31:09.462359 |
| E5 入口记录的服务镜像标签 | `course1027-draft:241250011` |
| 模型平台 / 版本 | DeepSeek / DeepSeek V4.1 Flash，按本人交互来源记录填写 |
| 最终候选 | `error-02`，本次网页交互取得，`is_recorded_replay=false` |

本次实验使用 Tiny Greeting 教学样例，复现从真实构建失败中取得反馈、通过模型生成修复候选、比较候选并手工复建的流程。验收分为两个独立条件：候选 Dockerfile 能够完成构建；构建得到的同一镜像能够执行目标程序，退出码为 0，标准输出为 `hello E3`。

上次保存在旧 `E5/work/` 中的环境自检、4 项单测和冒烟记录实际属于 E4，迁移后保存在 `E4/work/`。本报告使用本次新的 E5 证据，不将 E4 冒烟摘要作为 E5 的完整原始构建日志。

## 2. 实验输入与初始构建

项目构建输入为 `main.c`、`Makefile` 等文件，构建命令为 `make`，目标程序为 `./hello`。本次实际初始 Dockerfile 保存于证据目录的 `iter-01/Dockerfile`：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

初始输入固定基础镜像及 digest，复制项目文件后直接执行 `make`，没有增加构建工具的安装步骤。

在服务器 E5 目录执行采集入口，使用新的输出目录保留本次输入、命令、日志和提示：

```bash
python3 scripts/course.py e5 \
  --out work/e5-zyl-20261101-103032 \
  --build-timeout 1200
```

`invocation.json` 记录轨道为 `B`、阶段为 `e5`、入口为 `cloud-v1`、`replay=false`。`source-commit.txt` 保存本次实验的完整源码 SHA。

## 3. 初始失败与错误定位

`iter-01/result-retry.json` 记录：

```json
{"build_exit_code": 1}
```

执行 `grep -n 'make: not found' iter-01/build-retry.log`，得到两处匹配：

```text
30:#8 0.324 /bin/sh: 1: make: not found
34:0.324 /bin/sh: 1: make: not found
```

日志表明初始构建已执行到 `RUN make`，失败来自构建环境缺少 `make`，不是镜像拉取或网络连接错误。相同错误在构建步骤输出及摘要中重复出现，不能将两处匹配计为两次独立实验。

外层 Docker 构建退出码为 `1`。`entry-exit-code.txt` 则记录 E5 采集入口退出码为 `0`：采集入口成功识别并保存预期的缺 make 失败，随后生成模型提示。这两个退出码分别对应被测构建和证据采集流程，含义不同。

## 4. 两类提示与候选保存

本次使用 DeepSeek 网页进行两次独立对话：错误驱动提示提供实际初始 Dockerfile 和构建失败日志；上下文驱动提示在此基础上增加项目 README。每类提示请求三个候选，共保存六份 Dockerfile。

采集脚本生成的提示原本要求一个候选，实际发送的提示副本调整为请求三个完整候选。脚本原始提示保留在 `iter-01/`，实际发送版本及完整原始回复分别保存在：

| 提示类型 | 实际发送提示 | 原始回复 | 候选编号 |
|---|---|---|---|
| 错误驱动 | `model/error/prompt.txt` | `model/error/model-response.txt` | `error-01/02/03` |
| 上下文驱动 | `model/context/prompt.txt` | `model/context/model-response.txt` | `context-01/02/03` |

上表路径均相对于本次证据目录。候选 Dockerfile 从原始回复中单独提取，保存到 `candidates/<编号>/Dockerfile`，不包含 Markdown 代码围栏。选定候选的来源记录日期为 `2026-11-01`，平台为 `DeepSeek`，模型版本按本人记录为 `DeepSeek V4.1 Flash`，`manual_changes=[]`，表示没有记录对该候选 Dockerfile 的人工内容修改。具体模型交互时分秒未在本报告所据记录中提供。

## 5. 候选比较与选择

### 5.1 六份候选的差异

六份候选均保留相同的固定 `FROM`、`WORKDIR /work`、`COPY main.c Makefile ./`、`RUN make` 和 `CMD ["./hello"]`。依赖安装均位于 `COPY` 之后、`RUN make` 之前，且都使用 `--no-install-recommends` 并清理 `/var/lib/apt/lists/*`。

| 候选 | 显式安装的软件包 | 清理 apt 索引 | 主要差异 |
|---|---|---|---|
| `error-01` | `make gcc libc6-dev` | 是 | 显式列出 Make、GCC 和 C 库开发包 |
| `error-02` | `build-essential` | 是 | 使用构建工具元包；归一化后与 `context-01` 相同 |
| `error-03` | `make gcc` | 是 | 未显式列出 C 库开发包，其实际可用性须通过构建检验 |
| `context-01` | `build-essential` | 是 | 与 `error-02` 的差别仅为续行书写方式 |
| `context-02` | `gcc libc6-dev make` | 是 | 软件包集合与 `error-01` 相同，参数顺序不同 |
| `context-03` | `build-essential make gcc` | 是 | 同时指定构建工具元包及 `make`、`gcc` |

### 5.2 归一化规则和 R1—R4

本次将两类提示产生的六份候选合并比较。比较规则是：将反斜杠续行合并为空格，去除行首、行尾空白，合并连续水平空白；保留 Dockerfile 指令顺序和参数顺序，不对软件包参数重新排序。

- **R1：历史尝试检查。**本次提供的证据未单独记录选择前的候选构建历史，因此不据此推断已完成历史去重。本报告记录的是六份候选比较及选定 `error-02` 后的成功构建。
- **R2：候选一致性。**归一化后，`error-02` 与 `context-01` 完全一致，出现 2 次；其余规范化文本各出现 1 次。该组是出现次数最多的相同候选组，占全部候选的 2/6，并非超过半数。来源记录据此将该组作为优先方案，以 `error-02` 为实际构建输入。
- **R3：修复关联检查。**选定候选在 `RUN make` 前增加构建依赖安装，同时保留原始项目复制、构建和启动指令。它没有将 `RUN make` 替换为跳过构建的命令，也没有以打印答案替代目标程序。
- **R4：额外模型裁决。**本次来源记录依据 R2 选择优先组，没有记录独立的 R4 裁决步骤。

`error-01` 与 `context-02` 虽有相同的软件包集合，但参数顺序不同，按上述文本规则不计为同一规范化候选。六份候选的比较由实验交流中的助手辅助整理，最终选择及理由保存在候选来源记录中。

### 5.3 最终候选

选定文件为 `candidates/error-02/Dockerfile`：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN make
CMD ["./hello"]
```

通过 `sha256sum` 得到候选文件 SHA256：

```text
92d1cb0b766427c2d598a0641f03b2e04bc702bfb3e9d7bda4541fd88b17d92c
```

该哈希与 `来源记录.json` 的 `candidate_sha256` 一致。相对于初始 Dockerfile，修改是在 `RUN make` 前增加依赖安装和 apt 索引清理，原有项目构建及运行指令保持不变。

## 6. 手工构建结果

选定候选以本次采集的 `project/` 为构建上下文进行手工构建，对应镜像标签为：

```text
course1027-e5-candidate:241250011-20261101-143958
```

对应的构建操作为：

```bash
docker build --progress=plain \
  -f work/e5-zyl-20261101-103032/candidates/error-02/Dockerfile \
  -t course1027-e5-candidate:241250011-20261101-143958 \
  work/e5-zyl-20261101-103032/project
```

本次终端输出显示构建退出码为 `0`，依赖安装、项目复制和 `RUN make` 均命中已有构建缓存。日志节选为：

```text
#7 [4/5] RUN apt-get update && apt-get install -y --no-install-recommends build-essential     && rm -rf /var/lib/apt/lists/*
#7 CACHED
#8 [3/5] COPY main.c Makefile ./
#8 CACHED
#9 [5/5] RUN make
#9 CACHED
...
#10 naming to docker.io/library/course1027-e5-candidate:241250011-20261101-143958 done
#10 unpacking to docker.io/library/course1027-e5-candidate:241250011-20261101-143958 done
```

这次构建是复用缓存后的成功构建，不作为首次依赖安装耗时或无缓存构建性能的数据。未对另外五份候选逐一进行构建成功率测试，因此不据本次结果比较六份候选的实际成功率。

## 7. 同一镜像的功能验证

通过 `docker image inspect` 读取本次标签的镜像 ID，得到：

```text
sha256:e9945ea5a570bbc07849cd763afa9f37d3771f1738677baa15047fbf41ff6316
```

该值保存在 `candidate-image-id.txt`，镜像详情保存在 `candidate-image-inspect.json`。功能验证使用同一个镜像 ID，实际命令为：

```bash
docker run --rm \
  --network none \
  --cpus 1 \
  --memory 256m \
  --pids-limit 64 \
  sha256:e9945ea5a570bbc07849cd763afa9f37d3771f1738677baa15047fbf41ff6316
```

命令以禁网、1 CPU、256 MiB 内存和 64 进程上限运行目标镜像。运行命令、标准输出、标准错误和退出码分别保存在 `verify-command.txt`、`verify.log`、`verify-stderr.log` 和 `verify-exit-code.txt`。终端结果为：

```text
程序退出码：0
标准输出：
hello E3
标准错误：
```

| 检查项 | 实际结果 |
|---|---|
| 候选构建退出码 | `0` |
| 程序运行镜像 | 与成功构建标签 inspect 得到的镜像 ID 相同 |
| 程序退出码 | `0` |
| 标准输出 | `hello E3`，末尾换行 |
| 标准错误 | 空 |
| 功能判定 | 满足本次 Tiny Greeting 样例预期 |

因此，本次选定候选不仅得到可用镜像，也通过了目标程序的实际运行验证。

## 8. 本人工作、参考来源与实验限制

本人完成了个人实验目录下的 E5 初始失败采集、网页模型交互、原始回复及候选保存、来源记录填写、选定候选手工构建，以及按生成镜像 ID 进行程序验证。实验命令、候选比较和报告整理参考组内 B 组操作手册，并使用助手交流进行辅助。

服务、样例及证据采集脚本来自教学参考代码；本次没有将这些已有脚本作为本人新编写的算法。本次候选通过网页取得，没有调用模型 API；实验记录中的 `replay=false` 与 `is_recorded_replay=false` 表明该候选不是直接采用包内已保存的 DeepSeek 候选。

本次只验证一个固定的小型 C 项目及一个选定修复候选，不能代表完整论文基准结果或所有项目的构建成功率。候选生成和选择通过网页及人工操作完成，根因定位采用教学脚本对实际日志进行处理；尚未以本次实验证明自动模型调用、多轮自主修复或跨服务集成。E6、E7 的自动工作流和 CI 门禁属于后续阶段，不列为本次已完成内容。

本报告的结果依据本人提供的终端输出和来源 JSON 整理，未重新运行服务器实验。完整原始提示、模型回复及构建日志保存在服务器证据目录，尚未作为本报告附件交付。没有提供的本次环境自检输出、服务基线测试日志、R1 历史尝试记录及精确模型交互时间，不由旧 E4 记录或其他同学结果代填。

## 9. 证据索引

以下路径相对于 `/root/241250011/B08-remote-repo/E5/work/e5-zyl-20261101-103032`。其中候选构建日志使用实际操作中生成的带时间戳文件名，索引中的 `*` 表示该文件名部分，核验时应对应镜像标签及实际退出码文件。

| 证据路径 | 内容 |
|---|---|
| `source-commit.txt` | 实验源码 SHA：`a1d731a2418c7f545e2c0600083d3220b9f2d3bb` |
| `invocation.json` | B/e5、UTC 采集时间、入口与服务标签 |
| `entry-exit-code.txt` | E5 采集入口退出码 `0` |
| `project/` | 本次项目构建上下文 |
| `iter-01/Dockerfile` | 实际初始 Dockerfile |
| `iter-01/result-retry.json` | 初始 Docker 构建退出码 `1` |
| `iter-01/build-retry.log` | 初始合并日志，第 30、34 行包含缺 make 错误 |
| `iter-01/build/` | 入口保存的初始构建命令、标准输出、标准错误及退出码 |
| `iter-01/prompt-error-driven.txt`、`prompt-context-driven.txt` | 脚本生成的提示 |
| `model/error/prompt.txt`、`model-response.txt` | 实际错误驱动提示及原始回复 |
| `model/context/prompt.txt`、`model-response.txt` | 实际上下文驱动提示及原始回复 |
| `candidates/*/Dockerfile` | 六份候选 Dockerfile |
| `candidates/error-02/来源记录.json` | 选定候选的模型、日期、来源路径、哈希与选择理由 |
| `candidate-build*.log` 及对应退出码文件 | 选定候选构建日志及退出码 `0` |
| `candidate-image-tag*.txt` | 构建操作保存的镜像标签 |
| `candidate-image-id.txt` | 本次验证使用的镜像 ID |
| `candidate-image-inspect.json` | 对应标签的镜像详情 |
| `verify-command.txt` | 同镜像 ID 的程序验证命令 |
| `verify.log`、`verify-stderr.log` | 程序标准输出及空的标准错误 |
| `verify-exit-code.txt` | 程序退出码 `0` |
