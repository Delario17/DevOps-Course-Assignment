# E5 B组：失败反馈、模型候选与手工复建

## 基本信息

- 姓名：盛浩宇；学号：241250008；小组：B08。
- 实际执行日期：2026-11-02T12:57:35+08:00（北京时间）。
- 仓库：https://github.com/Delario17/DevOps-Course-Assignment
- 被测源码SHA：`7a0790fabd55d120c0a90fb40eaa788124c1c38b`。报告提交产生的新SHA与被测版本分别记录。
- 个人分支：`student/241250008/e5`。
- 个人实验位置：`/root/241250008/B08-remote-repo/E5`。
- 操作说明：本次由当前Codex对话助手按本人授权通过SSH代办，不将助手操作写成本人手工完成。

## 1. E4旧记录整理

旧仓库SHA为`24dbe7febf9fa43e38b5fa148af49fb729d96f32`，旧E5实际是E4环境。先备份并下载本人电脑，再重新克隆最新版，将旧E5/work恢复到新E4/work；逐文件比较一致。

- 服务器备份：`/root/241250008/backups/20261102-before-reclone/`。
- work归档SHA256：`9b20c0f0595ed2326d745df86f3a8a00acd69901c176fc260241360722e9351f`。
- 旧仓库归档SHA256：`299a60c3fc802a18d875fae63604e19903663b1025e7f7722b3daf81e9bcd4ef`。
- 旧checkout保存在上述备份目录的`old-checkout/`，未永久删除。
- 服务器GitHub连接超时；本机克隆后经完整Git bundle传入服务器重新克隆，origin恢复本组GitHub地址。
- 仅修改本人学号目录，未删除其他学号目录，未修改共享Docker配置，未清理其他人的镜像或容器。

## 2. 目标、环境与服务构建

复现真实构建失败，依据错误与项目上下文生成、选择Dockerfile候选，手工构建并验证实际镜像中的程序。

| 项目 | 实测 |
|---|---|
| 系统、架构 | Ubuntu 22.04.5 LTS，x86_64 |
| CPU / 可见内存 | 2 / 1.7 GiB |
| Docker Engine | 29.1.3 |
| Python | Python 3.10.12 |
| 自检 | problems=[]，通过；资源建议值warnings保留 |
| 服务构建及单测 | 整体退出0；24 passed |

本组代码最低可见内存要求为1.5 GiB，本次未修改门槛。命令在个人E5目录执行：

```bash
python3 scripts/doctor.py --out work/doctor-241250008/env.json
python3 scripts/course.py build --out work/build-241250008-01 --build-timeout 1200
python3 scripts/course.py e5 --out work/e5-241250008-01 --build-timeout 1200
```

## 3. 初始失败

实际初始输入：

```dockerfile
FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

初始Docker构建退出`1`，镜像内部make缺失导致127；E5采集入口退出0，表示正确采集目标失败并生成提示。实际日志行号：

```text
30: #8 0.160 /bin/sh: 1: make: not found
34: 0.160 /bin/sh: 1: make: not found
```

根因是基础镜像没有GNU Make。C项目还需要编译器和C库头文件。网络失败不能替代本实验的缺make目标错误。

## 4. 两类提示与候选来源

错误驱动提示包含Dockerfile和真实日志；上下文驱动另加README，明确C compiler、GNU Make、`./hello`和`hello E3`要求。

实际提示保存在服务器个人E5目录的 `work/e5-241250008-01/iter-01/prompt-error-driven.txt` 和 `prompt-context-driven.txt`。本PR只提交报告，原始提示和回复保存在个人服务器及电脑备份，不随PR提交。

来源为OpenAI当前Codex对话助手，精确服务模型版本未记录。助手阅读真实证据后，在同一对话上下文按两类提示组织六份候选。**没有六次独立网页/API采样，类别之间共享上下文，不据此比较模型成功率或上下文提示效果。**

各目录保存Dockerfile、对应提示、助手生成的代码回复内容和provenance.json；这是助手输出的文件化记录，不是外部网页聊天导出。生成时error-01与包内DeepSeek参考候选内容相同，原样保存在Dockerfile.model-original。官方Debian源下载停滞后，助手在实际候选中切换课程清华源并加入IPv4、重试和超时参数，保留FROM及项目指令；原始回复未改，不作为独立创新。

| 候选 | 提示类别 | 修复方案 | SHA256 |
|---|---|---|---|
| context-01 | 上下文驱动 | build-essential | `1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e` |
| context-02 | 上下文驱动 | build-essential | `1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e` |
| context-03 | 上下文驱动 | gcc + make + libc6-dev | `6d7f5aa4486ac581c557a63382e98d4c969e5768c8e13f74cd7d7516881bc353` |
| error-01 | 错误驱动 | build-essential | `cc9e790c86259c95ff55819042c0f143a465e212b5dd6ee91dd868ad87627cae` |
| error-02 | 错误驱动 | gcc + make + libc6-dev | `6d7f5aa4486ac581c557a63382e98d4c969e5768c8e13f74cd7d7516881bc353` |
| error-03 | 错误驱动 | build-essential | `1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e` |

六份原始内容保存在服务器个人E5目录的 `work/candidates-241250008/` 及电脑备份中。仅最终选定候选经过本次真实构建；其余仅文本检查，没有声称均已运行成功。

## 5. R1—R4与最终方案

- R1：本轮此前没有构建过这些修复候选，无需排除。
- R2：合并反斜杠续行、折叠连续空白，比较网络适配前的逻辑指令。build-essential方案4份，显式gcc/make/libc6-dev方案2份；计数仅描述本次批量方案，非独立采样。
- R3：两类都补make与C工具链，选择build-essential并保留固定FROM、WORKDIR、COPY、RUN make、CMD。
- R4：前述步骤已确定，无额外选择模型调用。
- 最终选`error-01`。助手补充清华Debian源及下载参数，原始模型Dockerfile与回复另存，实际构建文件及哈希按调整后记录。第一轮官方源构建因下载停滞取消，日志`candidate-build-01.log`和状态另存；第二轮完整成功日志为`candidate-build.log`。

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

## 6. 构建与程序验证

```bash
docker build --progress=plain -f work/candidates-241250008/error-01/Dockerfile -t course1027-e5-candidate:241250008 work/e5-241250008-01/project
docker image inspect course1027-e5-candidate:241250008 --format '{{.Id}}'
docker run --rm --network none --cpus 1 --memory 256m --pids-limit 64 镜像ID
```

完整实际运行参数在`work/e5-241250008-01/verify-command.json`。

| 检查 | 实测 |
|---|---|
| 候选构建退出码 | 0 |
| 实际镜像ID | `sha256:1827eda417e78fc61b394516f83ff81f703d42574fe5d133b5a0f90e88bd60a3` |
| 程序退出码 | 0 |
| stdout | `hello E3`加换行 |
| stderr | 空 |

构建成功与程序正确分别验证，运行使用本次镜像完整ID，避免标签误指向旧镜像。

## 7. 方法对应与限制

对应“失败反馈→生成/选择Dockerfile→真实构建→程序验证”。项目为课程Tiny Greeting样例，不是论文原始基准。本次采用助手批量候选及手工命令，没有复现独立随机采样、全论文数据集或效果统计。缓存与网络会影响耗时，本次不据耗时评价方法。

本次只做E5；未将E6/E7自动工作流、门禁和CI演示写作已完成。若教师明确要求独立网页交互，应本人按保存的原提示补做真实对话并附记录。

## 8. 证据索引

路径相对E5：

| 内容 | 路径 |
|---|---|
| 环境 | `work/doctor-241250008/env.json` |
| 构建、镜像、24项测试 | `work/build-241250008-01/` |
| 本次版本、初始输入、失败、提示 | `work/e5-241250008-01/` |
| 六份候选和来源 | `work/candidates-241250008/` |
| 选择理由 | `work/e5-241250008-01/candidate-selection.json` |
| 候选构建 | 同目录`candidate-build.log`、`candidate-build-exit-code.txt` |
| 镜像和运行 | 同目录`candidate-image-id.txt`、`candidate-image-inspect.json`、`verify-command.json`、`verify.log`、`verify-exit-code.txt` |
| 本机精简证据备份（不提交GitHub） | 本人电脑的 `E5-20261102/shy-e5-b-evidence/` |

本次Git提交仅包含 `E5/docs/shy-e5-b.md`。work及精简证据均不随PR提交，完整记录已另行归档下载本人电脑，服务器原始记录继续保留。上表证据路径是个人服务器或电脑上的定位信息，不是GitHub仓库中的附件链接。其他同学报告保持原样。

## 9. 分工和AI使用

本人提供学号、访问授权及组长要求。教学实现来自小组参考代码；目录备份迁移、克隆、候选整理、命令执行、日志核验和报告整理由当前助手代办。本报告保存真实结果，供本人阅读理解和现场解释，不声明本人独立手工完成。

## 10. 提交前核验

当前E5已跟踪文件扫描通过。历史扫描的两条命中来自原仓库E4命令手册的同一个教学假密钥示例，已确认非本次报告泄漏；未修改历史。本次只提交报告，work中原始记录保持不变；Git差异应仅新增本报告文件。
