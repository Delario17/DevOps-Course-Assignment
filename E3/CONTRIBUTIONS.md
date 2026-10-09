# MDFixer HYBRID 案例个人贡献

本文件只记录这一块案例，不代表整个 B08 E3 分工。

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
| 个人复现证据提交 SHA | 本次材料保存为 Git 提交后，按实际 SHA 回填 |

本地 Git 使用已有配置的提交身份。Git 作者信息与实验实际执行者分别记录；本轮自动实验不能标为本人手工执行。

姓名、学号和 GitHub 账号与既有 E2/CONTRIBUTIONS.md 一致。本人的 E3 实际贡献为发起并完成 Linux 脚本复现、提供实际结果并阅读确认辅助核查结论；参考补丁和验证脚本由 Codex 辅助编写，不将其描述为本人独立手写。
