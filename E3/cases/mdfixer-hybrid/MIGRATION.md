# MDFixer HYBRID 目录迁移

HYBRID 产物由 E3 公共 `fixtures/`、`oracle/`、`patches/`、`scripts/` 和 `evidence/` 迁入 `E3/cases/mdfixer-hybrid/`。固定 fixture 提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` 保留旧路径，脚本通过 Oracle 中的 `fixed_commit_working_directory` 核对其 Git blob。

2026-10-09 的三次历史证据和 2026-10-12 的回归证据均位于本案例 `evidence/`。旧 Hybrid/Target 联合迁移完整性记录保存在 [`../../integration-history/20261012-hybrid-target-layout-validation.json`](../../integration-history/20261012-hybrid-target-layout-validation.json)。
