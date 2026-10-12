# MDFixer TARGET 目录迁移

Target 产物原收纳在 `E3/cases/mdfixer-hybrid/target/`，现独立为 `E3/cases/mdfixer-target/`。fixture、Oracle、补丁、脚本和两次证据一起迁移，历史 evidence 文件保持原字节。

| 迁移前 | 当前 |
|---|---|
| `E3/cases/mdfixer-hybrid/target/fixture/` | `E3/cases/mdfixer-target/fixture/` |
| `E3/cases/mdfixer-hybrid/target/oracle/` | `E3/cases/mdfixer-target/oracle/` |
| `E3/cases/mdfixer-hybrid/target/patches/` | `E3/cases/mdfixer-target/patches/` |
| `E3/cases/mdfixer-hybrid/target/scripts/` | `E3/cases/mdfixer-target/scripts/` |
| `E3/cases/mdfixer-hybrid/target/evidence/` | `E3/cases/mdfixer-target/evidence/` |

固定提交 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954` 保留迁移前路径。Oracle 的 `fixed_commit_working_directory` 用于核对 Makefile、源码和头文件，迁移后更新的 README、SOURCE 由 Oracle SHA-256 固定。双案例旧布局的联合完整性记录保存在 [`../../integration-history/20261012-hybrid-target-layout-validation.json`](../../integration-history/20261012-hybrid-target-layout-validation.json)。
