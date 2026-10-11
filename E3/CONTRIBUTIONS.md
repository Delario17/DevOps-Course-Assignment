# 盛浩宇：MDFixer Hybrid 与 Target 个人贡献

本文件记录盛浩宇负责的 Hybrid 收尾和 Target 案例；最终四人贡献表由汇总负责人整合。

## Hybrid 历史贡献（2026-10-09）

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
| 个人复现证据提交 SHA | `e9e59b6a017d179ba5e845203c1665ad8450cf37`，包含本人复现证据、身份记录和辅助审阅确认；SHA 回填已完成于 `f1fe71cbcc1826bf33e8f7545bd11de913f9cc0b` |

本地 Git 使用已有配置的提交身份。Git 作者信息与实验实际执行者分别记录；本轮自动实验不能标为本人手工执行。

姓名、学号和 GitHub 账号与既有 E2/CONTRIBUTIONS.md 一致。原 Hybrid 阶段本人的实际贡献为发起并完成 Linux 脚本复现、提供实际结果并阅读确认辅助核查结论；参考补丁和验证脚本由 Codex 辅助编写，不将其描述为本人独立手写。

## 新分工补充（2026-10-11）

| 项目 | 记录 |
|---|---|
| 本次负责人 | 盛浩宇，241250008，lejuwujiang258 |
| 分工与分支 | Hybrid 收尾与 Target 声明案例；`b08/e3-mdfixer-target` |
| 原 Hybrid 合并 | [PR #2](https://github.com/Delario17/DevOps-Course-Assignment/pull/2)，main 合并版本 `59f45051ca7904247198b3aba6800b6f194333eb` |
| Hybrid 收尾 | 更新当前交付和操作说明；新增绑定原始输入哈希的 review.json；原 Fixture、Oracle 与三次证据保持不变 |
| Target 新材料 | 直接声明 Fixture、MD-only Oracle、参考/无效 Patch、独立验证脚本、日志、案例说明 |
| Target 固定提交 | `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`，包含 7 个版本固定的 Fixture 文件 |
| Target 实现及证据提交 | `fe788d6d6137024388e495fddda93242301fbff2`，包含 Oracle、Patch、执行脚本、44/44 实际证据及 Hybrid 状态文档收尾 |
| Target 实际执行者 | Codex；未记为盛浩宇本人发起复现 |
| Target 实际证据 | `evidence/mdfixer-target/20261011T110959885929+0800/`，44/44 PASS，39 条命令，配置 `b08-target-74f06528d5480265` |
| 新材料审阅状态 | 盛浩宇于 2026-10-11 阅读并明确确认 Target 的 Codex 辅助核查结论；APPROVED_WITH_AI_ASSISTED_REVIEW，见 HUMAN_REVIEW.md 与 Target review.json |
| AI 使用 | 用户请求并指定分工，Codex 辅助编写、执行及核查；原 A08 归属沿用 SOURCE.md |

上述 SHA 为实际本地提交；Target 实现提交的 SHA 回填已完成于 `3a0620477becc98abfe141805e05004a0e0ce491`。本次个人确认原文为“已阅读并确认，请补齐记录”，不作为本人发起 Target 实验的证明。此个人贡献说明不代填其他成员的交付完成情况。
