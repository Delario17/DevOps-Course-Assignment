# B08 E3 贡献记录

## MDFixer HYBRID：盛浩宇

| 项目 | 填写或记录 |
|---|---|
| 实际贡献认领人 | 盛浩宇 |
| 学号与 GitHub 账号 | 241250008，lejuwujiang258 |
| 个人负责范围 | MDFixer HYBRID 固定输入、参考补丁、行为验证和拒绝恢复案例 |
| AI 辅助准备 | Codex 整理来源、编写脚本和材料，并在 Ubuntu WSL 执行首轮实验 |
| A08 复用 | 原始 Makefile、C 源码和头文件；归属见 `fixtures/mdfixer-hybrid/SOURCE.md` |
| 固定样例提交 | `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` |
| 首轮实际执行者 | Codex automated Linux execution; B08 human review pending |
| 首轮证据 | `evidence/mdfixer-hybrid/20261009T123151981838+0800/`，40/40 PASS |
| 最终脚本验证证据 | `evidence/mdfixer-hybrid/20261009T123645645063+0800/`，40/40 PASS |
| 本人后续复现 | 盛浩宇于 2026-10-09 13:37:14 至 13:37:39（北京时间）本人发起 Linux 脚本复现；`evidence/mdfixer-hybrid/20261009T133714630641+0800/`，40/40 PASS，39 条命令 |
| 复现时仓库提交 | `d293999a0c7af3674768f311ad53fc171e01c0aa` |
| 本次实际环境 | Ubuntu 24.04 WSL、x86_64、GCC 13.3.0、GNU Make 4.3、Python 3.12.3；`b08-hybrid-74f06528d5480265` |
| 本人审阅 | 盛浩宇已阅读 Codex 辅助检查结论，并在对话中明确回复“已阅读并确认一致”；详情见 `HUMAN_REVIEW.md` |
| 个人复现证据提交 SHA | `e9e59b6a017d179ba5e845203c1665ad8450cf37`，包含本人复现证据、身份记录和辅助审阅确认；随后单独提交本表 SHA 回填 |

本地 Git 使用已有配置的提交身份。Git 作者信息与实验实际执行者分别记录，自动实验执行者以 evidence 中的 operator 为准。

姓名、学号和 GitHub 账号与既有 E2/CONTRIBUTIONS.md 一致。盛浩宇的 E3 实际贡献为发起并完成 Linux 脚本复现、提供实际结果并阅读确认辅助核查结论；参考补丁和验证脚本由 Codex 辅助编写。

## DRAFT Tiny Greeting：王祎

| 项目 | 填写或记录 |
|---|---|
| 任务负责人 | 王祎 |
| 学号与 GitHub 账号 | 241250007，Delario17 |
| 负责范围 | DRAFT 固定项目、失败环境、参考环境、构建与功能验证基线 |
| 固定输入提交 | `5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43` |
| AI 辅助准备 | Codex 编写 Fixture、Oracle、Dockerfile、验证脚本和提交材料 |
| 准备阶段执行 | Codex 在 macOS 发起本机构建与功能验证，18/18 项断言通过 |
| 本人完整复现 | 王祎于 2026-10-12 10:53:58 至 11:02:33 发起 Docker 验证，24/24 PASS，19 条命令 |
| 最终证据 | `evidence/draft-tiny-greeting/20261012T105358976530+0800/` |
| 最终证据提交 | `acdea5f45ed6ab73c600b8ffb438f8e9605c2847` |
| 运行时仓库提交 | `312fdd9b63a0711defb4531545cd4caf639673c0` |
| 实际环境 | macOS 26.6.2 arm64、Python 3.12.14、Docker Desktop 4.94.0、Docker Engine 29.8.2 |
| 复现结果 | 失败镜像退出码 1；参考镜像成功；容器输出 `hello E3`，退出码 0 |
| 审阅 | Codex 应王祎请求核对完整证据，结论记录于 `DRAFT_REVIEW.md` |

王祎完成 DRAFT 的本人 Docker 复现并提交实际结果，Codex 辅助准备基线与核对证据。AI 准备、本人执行和辅助审阅分别记录。
