# B08 E3：MDFixer 混合声明修复基线

本目录当前交付一个 HYBRID 声明风格的 MDFixer 参考案例：固定 MD 输入、原始项目、参考补丁、失败候选，以及实际 Linux 验证和恢复记录。
它用于 E3 测试基线准备，不表示 MDFixer 自动修复服务已经实现，也不代表 B08 的 DRAFT 和其他声明风格已经完成。

## 已完成的这一块

| 内容 | 文件或目录 |
|---|---|
| 版本固定的故障项目 | `fixtures/mdfixer-hybrid/` |
| MD-only 人工参考输入及预期 | `oracle/mdfixer-hybrid.expected.json` |
| 参考修复 | `patches/mdfixer-hybrid.reference.patch` |
| 故意失败的候选 | `patches/mdfixer-hybrid.invalid.patch` |
| 一键行为验证与恢复 | `scripts/run_mdfixer_hybrid.py` |
| 最终脚本真实运行记录 | `evidence/mdfixer-hybrid/20261009T123645645063+0800/` |
| 个人操作与提交步骤 | `MANUAL_STEPS.md` |
| 贡献、AI 使用、人工审阅 | `CONTRIBUTIONS.md`、`AI_USAGE.md`、`HUMAN_REVIEW.md` |

固定样例在 B08 本地真实提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` 中；此提交必须与后续验证材料一起保留，合并时保留原始提交历史。
A08 源码归属与固定参考版本见 `fixtures/mdfixer-hybrid/SOURCE.md`。

## 为什么是 HYBRID

目标声明是 `build/main.o: src/main.c $(HEADERS)`，既有直接文件项，也有头文件变量项。
原 Makefile 的 HEADERS 漏掉 include/config.h，又额外声明 include/unused.h。参考补丁只在 HEADERS 加入 config.h，保留已有 RD。
本次不宣称所有 MD/RD 已消除。

## 成功标准及已观察结果

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

本次由 Codex 在现有 Ubuntu 24.04 WSL 中执行，40/40 项断言通过、39 条命令已记录。GCC 13.3.0、GNU Make 4.3、Python 3.12.3、x86_64，实测配置为 `b08-hybrid-74f06528d5480265`。
首次运行目录 `20261009T123151981838+0800/` 保留为历史证据；最终脚本将子进程环境限定为 Linux 默认 PATH 和固定语言设置，并再次通过 40/40。
人工审阅仍待本人确认。运行快照的 pending 标记保留执行时状态，后续人工确认另记 `HUMAN_REVIEW.md`。

## Linux 一键重跑

从本仓库根目录执行，工具需要 python3、gcc、make、git：

```bash
python3 E3/scripts/run_mdfixer_hybrid.py --operator "姓名（本人发起脚本复现）"
```

每次创建新的 evidence/mdfixer-hybrid/时间目录，不覆盖旧证据。
脚本先核对源码与固定提交一致，再复制到 Linux 临时目录执行实验；不在仓库源码上运行 make clean，也不把参考补丁永久应用到故障样例。
参考补丁和失败补丁的应用目录都是临时样例根目录，补丁路径中的 Makefile 指向该目录的 Makefile。
当前脚本仅使用 Python 标准库，不需要 pip 安装；Docker 不是此案例的运行前提。

## 输入和证据边界

oracle 文件是 E3 人工参考材料，包含来源、范围和待审阅状态；并未伪装为 BuildChecker 或 MDFixer 的真实服务输出。
reference-validation.json 的 ACCEPTED 和 rejected-candidate.json 的 REJECTED 是本脚本的参考验证决定。
本次证据不生成真实检测器报告或 API Job，也不修改已经通过评审的 E2 契约。
配置标识依据实际系统、架构、工具链与关键选项生成；源码 SHA 独立记录。WSL 运行没有镜像 ID。

## B08 组级任务仍需其他成员协调

- DRAFT 的失败环境、参考成功环境和功能验证。
- 其余直接声明、纯变量声明、隐式规则与 .d 文件案例。
- 本案例的成员贡献认领、人工审阅，以及组长整合与提交。
