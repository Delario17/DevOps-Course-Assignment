# MDFixer Hybrid 与 Target 审阅记录

## Hybrid：已确认

- 状态：APPROVED_WITH_AI_ASSISTED_REVIEW。
- 复现人及确认人：盛浩宇，241250008，GitHub：lejuwujiang258。
- 确认日期：2026-10-09（北京时间）。
- 本人复现时间：2026-10-09 13:37:14.630641 至 13:37:39.512063。
- 证据目录：`evidence/mdfixer-hybrid/20261009T133714630641+0800/`。
- 本人是否发起脚本重跑：是。本人在对话中报告已执行完成；运行记录 operator 为盛浩宇。
- 详细文件核查：由 Codex 应本人请求辅助完成。
- 技术检查结论：通过，40/40 项实验断言成功，39 条命令与原始日志一致。
- 本人确认依据：本人阅读辅助检查结论后，在对话中明确回复“已阅读并确认一致”。

## 已核对的技术事实（Codex 辅助核查，本人阅读确认结论）

- [x] main.c 实际读取 config.h，原 Makefile 的 HEADERS 未声明 config.h；GCC 依赖输出与 Make 数据库支持该判断。
- [x] 修复前 CONFIG_VALUE 4→5 的普通构建仍输出 10；相同源码完整重建输出 11。
- [x] 参考补丁只补 config.h，保留原有 unused.h RD，符合本案例限定的 MD 修复范围。
- [x] 修复后两次只改头文件均自动重编译，输出依次为 11、12；这两个增量阶段没有先 clean。
- [x] 故意失败候选退出码为 2，被拒绝后恢复有效 Makefile；恢复字节一致，重新构建和运行输出 12。
- [x] 固定源码提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` 与实际源码一致；运行时提交为 `d293999a0c7af3674768f311ad53fc171e01c0aa`。
- [x] 环境、源码、脚本、oracle 和补丁哈希均一致，README 各阶段输出与 observations.json 相符。
- [x] commands.txt 与 JSON 内 39 条命令的标准输出、错误输出和退出码一致；唯一非零退出对应预期的失败候选。
- [x] 个人身份来自既有 E2 贡献记录，AI 编写、AI 首轮执行和本人后续发起复现分别记录。

## 确认范围

本 HYBRID 参考案例已由本人发起脚本复现，经 Codex 辅助核查通过，本人已阅读并确认核查结论与运行结果一致。
此记录不声称本人逐条手工执行了脚本内命令，也不声称本人独立实现了 MDFixer 服务。
原始运行目录中的执行者、时间和 PENDING_HUMAN_REVIEW 保持执行时快照，不回写；本文件记录随后完成的个人确认。

## 当前 Hybrid 审阅入口（2026-10-11 整理）

当前状态仍为 APPROVED_WITH_AI_ASSISTED_REVIEW。本次新增 oracle/mdfixer-hybrid.review.json，绑定原始 Oracle 和已确认个人复现记录的 SHA-256；没有新增人工签名，也没有改写历史 pending 或执行记录。
原 Hybrid 已由 PR #2 合并 main，原确认继续有效。

## Target：已完成辅助审阅确认

- 当前状态：APPROVED_WITH_AI_ASSISTED_REVIEW。
- 确认人：盛浩宇，241250008，GitHub：lejuwujiang258。
- 确认日期：2026-10-11（北京时间）。
- 技术验收状态：PASS；44/44 项实验断言，39 条命令。
- 实际执行者：Codex automated Linux execution for Sheng Haoyu; Target human review pending。
- 运行时间：2026-10-11 11:09:59 至 11:10:07，北京时间。
- 固定样例提交：`b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`。
- 证据目录：`evidence/mdfixer-target/20261011T110959885929+0800/`。
- 辅助核查：Codex 对固定源码、脚本/Oracle/Patch 哈希、捕获补丁、命令与 JSON、阶段输出和精确恢复完成核对，均相符。
- 技术事实：修复前头文件 4→5 增量仍输出 10，完整重建为 11；修复后两次增量为 11、12，均重编译；无效候选退出码 2，被拒绝后恢复有效 Makefile，重建输出 12。
- 成员确认依据：盛浩宇阅读本次 Target 辅助核查结论后，在对话中明确回复“已阅读并确认，请补齐记录”。这是对 Target 的单独确认。
- 当前状态索引：`oracle/mdfixer-target.review.json`；原运行快照不回写。

盛浩宇已阅读并确认本次 Target 的 Codex 辅助核查结论。实际运行及详细文件核查由 Codex 完成；此记录不声明盛浩宇本人执行了本次 Target 实验。后续本人若重跑，另记实际执行事实和新的证据目录。
原始 Oracle 与运行证据中的 pending 保留准备/执行时状态；随后完成的确认以本文件及 oracle/mdfixer-target.review.json 为准。
