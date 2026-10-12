# Macro 个人目录迁移（2026-10-12）

本次要求：所有交付和后续变更只位于 `E3/cases/mdfixer-macro/`。以当前 `origin/main` 为基线建立 `b08/e3-mdfixer-macro-layout`，不带入旧分支的公共文件修改。

- [x] 从历史提交 `54ee1af68a9801cf723315b0c1efe3cddd4772e1` 提取 Macro Fixture、Oracle、Patch、验证器、统一入口和本人记录。
- [x] 历史统一入口的 107 个证据文件迁入 `evidence/history/`，字节和 SHA-256 保持不变；旧路径、提交和执行者仍是当时记录。
- [x] 个人忽略规则、属性规则、工具中间文件和新输出都限制在本目录。
- [x] 统一入口读取相邻案例的 `scripts/run.py`；Target 兼容当前 `mdfixer-hybrid/target/` 和独立 `mdfixer-target/`。所有新证据由 `--output` 收集到本目录。
- [x] 创建本目录 Fixture 的新固定提交 `83354f218a03a2085b4e571582f8d333d3a4ddf3`，更新 Oracle；验证不依赖已删除的旧 Macro 分支。
- [x] 重跑 12 项入口测试、完整四类案例 164/164；核对历史证据和 Git 修改范围，详见 `MIGRATION_VALIDATION.json`。
- [x] 推送 `b08/e3-mdfixer-macro-layout`，对最新 main 执行 `git merge-tree --write-tree origin/main HEAD`，结果无冲突。

组级 README、贡献索引、AI 记录和其他成员目录由集成负责人维护，本分支对它们不产生差异。

交付实现提交为 `5869c2a`，固定 Fixture 提交为 `83354f2`；随后单独记录本页的推送完成状态。迁移分支可用于组级整合，合并时保留 Fixture 提交历史。
