# B08 E3：并行测试基线

本目录当前交付两条独立基线：DRAFT Tiny Greeting 环境生成案例，以及 HYBRID 声明风格的 MDFixer 参考修复案例。

| 基线 | 当前结果 | 入口 |
|---|---|---|
| DRAFT Tiny Greeting | 本机构建与功能验证 18/18 通过；Docker 复现待完成 | `DRAFT_BASELINE.md` |
| MDFixer HYBRID | Linux 复现 40/40 通过，人工确认完成 | 本文后续章节 |

## DRAFT Tiny Greeting

DRAFT 基线包含固定项目、失败 Dockerfile、参考 Dockerfile、人工 Oracle、自动验证脚本和证据目录。失败环境与参考环境使用同一基础镜像 digest，核心判据是环境能否完成构建并让容器输出 `hello E3`。

- 说明：`DRAFT_BASELINE.md`
- 固定输入：`fixtures/draft-tiny-greeting/`
- Oracle：`oracle/draft-tiny-greeting.expected.json`
- 验证脚本：`scripts/run_draft_baseline.py`
- 当前证据：`evidence/draft-tiny-greeting/20261011T141102041611+0800/`
- 复现审阅：`DRAFT_REVIEW.md`

当前 macOS 机器没有 Docker，因此已保存本机构建成功和 Docker 不可用的真实记录。最终容器复现命令：

```bash
python3 E3/scripts/run_draft_baseline.py --operator "姓名" --docker required
```

## MDFixer HYBRID

该案例包含固定 MD 输入、原始项目、参考补丁、失败候选，以及实际 Linux 验证和恢复记录。验收范围是参考补丁行为，MDFixer 自动修复服务安排在后续实验。

### 已完成内容

| 内容 | 文件或目录 |
|---|---|
| 版本固定的故障项目 | `fixtures/mdfixer-hybrid/` |
| MD-only 人工参考输入及预期 | `oracle/mdfixer-hybrid.expected.json` |
| 参考修复 | `patches/mdfixer-hybrid.reference.patch` |
| 故意失败的候选 | `patches/mdfixer-hybrid.invalid.patch` |
| 一键行为验证与恢复 | `scripts/run_mdfixer_hybrid.py` |
| 最终脚本真实运行记录 | `evidence/mdfixer-hybrid/20261009T123645645063+0800/` |
| 盛浩宇本人发起的复现记录 | [`个人复现 README`](evidence/mdfixer-hybrid/20261009T133714630641+0800/README.md)、[`完整 observations.json`](evidence/mdfixer-hybrid/20261009T133714630641+0800/observations.json) |
| 个人操作与提交步骤 | `MANUAL_STEPS.md` |
| 贡献、AI 使用、人工审阅 | `CONTRIBUTIONS.md`、`AI_USAGE.md`、`HUMAN_REVIEW.md` |

固定样例在 B08 本地真实提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` 中；此提交必须与后续验证材料一起保留，合并时保留原始提交历史。
A08 源码归属与固定参考版本见 `fixtures/mdfixer-hybrid/SOURCE.md`。

### 为什么是 HYBRID

目标声明是 `build/main.o: src/main.c $(HEADERS)`，既有直接文件项，也有头文件变量项。
原 Makefile 的 HEADERS 漏掉 include/config.h，又额外声明 include/unused.h。参考补丁只在 HEADERS 加入 config.h，保留已有 RD；本轮验收范围为 config.h 的 MD 修复。

### 成功标准及已观察结果

| 阶段 | 标准 | 2026-10-09 实际结果 |
|---|---|---|
| 初始完整构建，CONFIG_VALUE=4 | 输出 10 | 10 |
| 修复前改为 5，不 clean | 仍输出 10，产物未更新 | 10 |
| 相同源码完整重建 | 输出 11 | 11 |
| 参考修复后恢复 4，完整构建 | 输出 10 | 10 |
| 修复后改为 5，不 clean | 重编译，输出 11 | 11 |
| 修复后再改为 6，不 clean | 再次重编译，输出 12 | 12 |
| 加入 false 失败候选 | 构建非零，拒绝候选 | 退出码 2，REJECTED |
| 恢复候选应用前的有效 Makefile | 字节一致，构建及运行通过 | 输出 12，PASSED |

首轮与最终脚本验证由 Codex 在现有 Ubuntu 24.04 WSL 中执行，均为 40/40 项断言通过、39 条命令已记录。GCC 13.3.0、GNU Make 4.3、Python 3.12.3、x86_64，实测配置为 `b08-hybrid-74f06528d5480265`。
首次运行目录 `20261009T123151981838+0800/` 保留为历史证据；最终脚本将子进程环境限定为 Linux 默认 PATH 和固定语言设置，并再次通过 40/40。
盛浩宇于 2026-10-09 13:37 本人发起同一脚本复现，结果为 40/40 PASS，39 条命令有完整日志；上述结果表与本次个人运行一致。Codex 应本人请求核对 README、JSON、命令日志、补丁快照和哈希，技术证据均通过。
盛浩宇已阅读并明确确认辅助核查结论与本人运行结果一致，个人确认记录见 `HUMAN_REVIEW.md`。运行快照中的 pending 标记保留执行时状态，不回写历史日志。

### Linux 一键重跑

从本仓库根目录执行，工具需要 python3、gcc、make、git：

```bash
python3 E3/scripts/run_mdfixer_hybrid.py --operator "姓名（本人发起脚本复现）"
```

每次创建新的 evidence/mdfixer-hybrid/时间目录，不覆盖旧证据。
脚本先核对源码与固定提交一致，再复制到 Linux 临时目录执行实验；不在仓库源码上运行 make clean，也不把参考补丁永久应用到故障样例。
参考补丁和失败补丁的应用目录都是临时样例根目录，补丁路径中的 Makefile 指向该目录的 Makefile。
当前脚本使用 Python 标准库，无需安装 pip 依赖，并直接调用 Linux 工具链完成验证。

### 输入和证据边界

oracle 文件是 E3 人工参考材料，包含来源、范围和待审阅状态；真实服务输出将在对应服务实验中单独生成。
reference-validation.json 的 ACCEPTED 和 rejected-candidate.json 的 REJECTED 是本脚本的参考验证决定。
本次证据覆盖参考补丁实验和候选拒绝恢复，E2 契约保持已评审版本。
配置标识依据实际系统、架构、工具链与关键选项生成；源码 SHA 独立记录。WSL 运行没有镜像 ID。

## B08 组级任务仍需完成

- 在 Docker 环境生成 DRAFT 失败镜像与参考镜像的最终 `PASS` 证据。
- 其余直接声明、纯变量声明、隐式规则与 .d 文件案例。
- 本案例的盛浩宇个人复现和确认已记录；组长负责整合与提交。
