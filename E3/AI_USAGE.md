# E3 MDFixer HYBRID AI 使用记录

- 工具：Codex。
- 日期：2026-10-09，Asia/Shanghai。
- 用户请求：完成一个 MDFixer 混合声明案例，并单独说明需要本人操作的准备和提交步骤。
- 输入资料：E3 课件、A08 已合并 E3 源码和证据、B08 已接受的 E2 契约。
- 参考 A08 版本：`f8584a58e7be9d39ca630b5c6617a9ed25e8e4da`。
- 源码差异：Makefile、main.c、common.h、config.h 与参考版本内容一致；unused.h 仅改写说明注释，空头文件和 RD 作用保持一致。
- 准备工作：更新 B08 远端引用；从 origin/main 创建本地 `b08/e3-mdfixer-hybrid` 分支；创建可追溯的 B08 故障样例提交。
- AI 编写：MD-only 参考输入、参考及无效补丁、Linux 验证与恢复脚本、README、操作步骤、贡献和待人工审阅记录。
- AI 实际执行：在 Ubuntu-24.04 WSL 中使用 GCC 13.3.0、GNU Make 4.3、Python 3.12.3 验证；结果为 40/40 PASS，39 条命令有原始输出和退出码。
- 实际行为：修复前增量 10、完整重建 11；修复后头文件两次变更分别得到 11、12；失败候选退出码 2 被拒绝，恢复后输出 12。
- 验证范围：已知参考补丁的行为与候选拒绝恢复；未运行真实 MDFixer 或 BuildChecker 服务，未声称所有 MD/RD 已修复。
- 首次证据：`evidence/mdfixer-hybrid/20261009T123151981838+0800/`。
- 最终脚本验证：将构建子进程限定为 Linux 默认 PATH 与固定语言设置后，再次得到 40/40 PASS；证据为 `evidence/mdfixer-hybrid/20261009T123645645063+0800/`。
- 首轮实际执行者：Codex；随后本人发起的复现和确认记录见下节。
- 提交范围：本地独立分支。未推送、创建 PR 或合并 main。
- 附带 E2 检查：尝试运行既有 E2/validate.py；当前 Windows Python 缺少 openapi_spec_validator，未完成该验收。E2 文件未修改；E3 脚本不需要任何 pip 依赖。

复用 A08 源码已标明原作者和仓库，新增 B08 材料及实验独立记录。没有将 AI 执行或起草的结果记为成员手工执行或人工确认。

## 本人复现和辅助补齐（2026-10-09）

- 盛浩宇本人发起脚本复现，记录时间为北京时间 13:37:14 至 13:37:39。
- 个人证据：`evidence/mdfixer-hybrid/20261009T133714630641+0800/`；operator 为盛浩宇，40/40 PASS，39 条命令。
- 本人随后请求 Codex 检查 README、observations.json，并补齐贡献和提交文档。
- Codex 辅助检查源码版本、各阶段输出、原始命令、退出码、补丁快照、恢复结果和哈希，全部相符。
- 本人身份沿用 E2 既有贡献记录：盛浩宇，241250008，lejuwujiang258。
- 本人在对话中明确回复“已阅读并确认一致”；HUMAN_REVIEW.md 据此记录本人确认，详细核查仍注明由 Codex 辅助完成。
- 本人发起的自动脚本复现与 AI 编写、AI 首轮自动执行区分记录。
- 原始运行 README 和 observations.json 未改写。新增个人证据及文档仅保存到本地任务分支；未推送或合并 main。
