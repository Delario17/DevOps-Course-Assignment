# E3 MDFixer Hybrid 与 Target AI 使用记录

## Hybrid 历史记录（2026-10-09）

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
- 首次证据：`evidence/20261009T123151981838+0800/`。
- 最终脚本验证：将构建子进程限定为 Linux 默认 PATH 与固定语言设置后，再次得到 40/40 PASS；证据为 `evidence/20261009T123645645063+0800/`。
- 首轮实际执行者：Codex；随后本人发起的复现和确认记录见下节。
- 当日提交范围：本地独立分支；在该记录生成时尚未推送、创建 PR 或合并 main。当前合并状态见 2026-10-11 记录。
- 附带 E2 检查：尝试运行既有 E2/validate.py；当前 Windows Python 缺少 openapi_spec_validator，未完成该验收。E2 文件未修改；E3 脚本不需要任何 pip 依赖。

复用 A08 源码已标明原作者和仓库，新增 B08 材料及实验独立记录。没有将 AI 执行或起草的结果记为成员手工执行或人工确认。

## 本人复现和辅助补齐（2026-10-09）

- 盛浩宇本人发起脚本复现，记录时间为北京时间 13:37:14 至 13:37:39。
- 个人证据：`evidence/20261009T133714630641+0800/`；operator 为盛浩宇，40/40 PASS，39 条命令。
- 本人随后请求 Codex 检查 README、observations.json，并补齐贡献和提交文档。
- Codex 辅助检查源码版本、各阶段输出、原始命令、退出码、补丁快照、恢复结果和哈希，全部相符。
- 本人身份沿用 E2 既有贡献记录：盛浩宇，241250008，lejuwujiang258。
- 本人在对话中明确回复“已阅读并确认一致”；REVIEW.md 据此记录本人确认，详细核查仍注明由 Codex 辅助完成。
- 本人发起的自动脚本复现与 AI 编写、AI 首轮自动执行区分记录。
- 原始运行 README 和 observations.json 未改写。在该记录生成时，新增个人证据及文档仅保存到本地任务分支，尚未推送或合并 main。后续合并状态见下节。

## 新分工实施（2026-10-11）

- 用户要求：按盛浩宇新分工完成 Hybrid 收尾与 Target 声明案例，在原工作上继续。
- 基础：已拉取并基于 B08 origin/main `59f45051ca7904247198b3aba6800b6f194333eb` 建立本地 `b08/e3-mdfixer-target`。原 Hybrid 已通过 PR #2 合并，原材料没有删除。
- Hybrid 状态：更新交付和操作文档；新增 review.json，将现有成员确认绑定到原 Oracle 和个人复现的哈希；不修改固定 Fixture、原 Oracle 和旧实验文件。
- Target 准备：复用有归属的 C 源码，将依赖改为直接声明并移除 unused.h，仅构造 config.h MD；固定 Fixture 提交 `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`。
- AI 编写：Target MD-only 参考输入、两个 Patch、从 Hybrid 脚本派生的独立 Target 执行脚本、案例说明、贡献及 PR 说明。
- AI 实际执行：Ubuntu-24.04 WSL，GCC 13.3.0、GNU Make 4.3、Python 3.12.3；`target/evidence/20261011T110959885929+0800/`，44/44 PASS，39 条命令。
- AI 辅助核查：固定提交与当前源码、输入/脚本哈希、命令输出与 JSON、Patch 快照、7 阶段行为、拒绝与恢复全部相符。
- Target 判断：原规则与参考规则均为直接文件声明；参考声明与 GCC -MM 项目依赖完全相等。没有项目内 RD。
- 人工确认：盛浩宇于 2026-10-11 阅读 Target 辅助核查结论后，明确回复“已阅读并确认，请补齐记录”；本次单独记录为 APPROVED_WITH_AI_ASSISTED_REVIEW，见 REVIEW.md 和 target/oracle/review.json。实际执行及详细核查仍记为 Codex。
- 代码边界：本次完成个人测试基线；没有实现真实 MDFixer 服务。统一运行入口由 Macro 负责人整合，DRAFT 和 Implicit 由相应成员负责。
- 发布状态：本次保存本地提交，尚未替用户推送、创建或合并新 PR。
- 实际提交：固定 Fixture 为 `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`；实现、证据及状态收尾为 `fe788d6d6137024388e495fddda93242301fbff2`；真实 SHA 回填已完成于 `3a0620477becc98abfe141805e05004a0e0ce491`。
- 提交前补齐：依据本人本次明确确认同步更新 README、审阅记录、贡献、验收清单和 PR 描述；所有原始 Oracle、Fixture、Patch、执行脚本与实验文件保持不变。

## 目录重组后的迁移（2026-10-12）

- 用户明确要求：先保存上次文件，拉取 main，写入本人负责的 mdfixer-hybrid 子文件夹，并说明新 PR 提交步骤。
- 先备份：原 HEAD 7e53650 的 tracked 文件完整 ZIP、全部引用与提交的 Git bundle、本地备份分支；bundle 已校验。
- 更新 main：fetch origin 后 fast-forward 到组长目录重组提交 d27dc4c；新建 b08/e3-mdfixer-hybrid-layout。
- 成员目录：全部改动仅位于 E3/cases/mdfixer-hybrid/，Target 作为 target/ 子案例。组级索引保持 main 原样，交由组长集成。
- 固定输入：Target 故障 Makefile、C 和头文件保留原字节，只更新 README/SOURCE 的迁移说明；独立提交为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`。现行 Oracle 绑定该提交与当前路径。
- 脚本适配：Target 使用本子案例的 fixture/oracle/patches/evidence 路径与 fixed_commit_working_directory；实验判据和恢复逻辑保持不变。Hybrid 使用 main 已适配的脚本。
- 历史证据：Hybrid 三次原证据、Target 一次原证据内容不改写。review.json 改为绑定原捕获输入及证据，同时单独标明当前 Oracle 哈希与迁移关系。
- 新 AI Linux 验证：Hybrid `evidence/20261012T144643089037+0800/`，40/40 PASS；Target `target/evidence/20261012T144600994684+0800/`，44/44 PASS；各 39 条原始命令。
- 人工事实：沿用既有真实日期和确认范围，不将 2026-10-12 的 AI 验证写成盛浩宇本人执行或新的人工签名。
- 发布状态：本次保存到新的本地分支，尚未替用户推送或创建新 PR。
- 实际迁移提交：`c192a41b9878106f47872239db2b7b55805ea97a`，固定 Fixture 为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`，贡献表独立回填实际 SHA。
