# B08 E3 AI 使用索引

Codex 用于构造固定输入、Oracle、参考/无效补丁、验证脚本、迁移适配和证据核对。个人执行与 AI 自动执行在案例记录中分别标注，原始 evidence 保留实际 operator、环境和时间。

| 案例 | AI 辅助内容 | 执行与审阅 | 详细记录 |
|---|---|---|---|
| DRAFT Tiny Greeting | C/Make fixture、两份 Dockerfile、Oracle、验证脚本、证据核对 | 王祎本人完成 Docker 复现，Codex 核对 24/24 结果 | [AI 记录](cases/draft-tiny-greeting/AI_USAGE.md) |
| MDFixer TARGET | 直接声明 fixture、MD-only Oracle、两类补丁、Linux 行为验证 | Codex 执行 44/44，盛浩宇确认核查结论 | [AI 记录](cases/mdfixer-target/AI_USAGE.md) |
| MDFixer MACRO | `$(DEPS)` 案例、两类补丁、单案例验证器、四类统一入口和入口测试 | 朱雨乐发起 Macro+Hybrid WSL 复现；Codex 执行四类 164/164 | [AI 记录](cases/mdfixer-macro/AI_USAGE.md) |
| MDFixer HYBRID | 来源整理、混合声明 Oracle、两类补丁、Linux 行为验证 | 盛浩宇本人执行 40/40 并确认，Codex 核对证据 | [AI 记录](cases/mdfixer-hybrid/AI_USAGE.md) |
| MDFixer IMPLICIT | 模式规则案例迁移、Oracle、两类补丁、Linux 行为验证 | Codex 执行 34/34；孙博一本人复现与确认待补 | [AI 记录](cases/mdfixer-implicit/AI_USAGE.md) |

四类统一验证的自动运行证据位于 [`cases/mdfixer-macro/evidence/suite/`](cases/mdfixer-macro/evidence/suite/)；各案例的个人复现与审阅状态以自身 `REVIEW.md` 为准。
