# 2026-10-12：迁入成员目录

本次基于 origin/main `d27dc4c`，分支 `b08/e3-mdfixer-hybrid-layout`。Git diff 仅涉及 E3/cases/mdfixer-hybrid/，不修改组级索引和其他成员案例。Target 作为本成员目录内的 target/ 子案例；若组长以后调整案例索引，可按此完整子目录继续移动。

## 已先完成备份

旧分支 b08/e3-mdfixer-target 和本地 backup/e3-mdfixer-target-before-layout-20261012 均保留，原 HEAD 为 `7e53650fa3799e899c318e4d66bc857b0ec28913`。
本机备份位于实验论文/backups/mdfixer-before-layout-20261012-7e53650/，包含 previous-files.zip、previous-repository.bundle 和 README.txt；bundle 已校验，保留完整历史。备份不纳入作业 PR。

## 路径映射（相对于仓库根目录）

| 迁移前 | 当前 |
|---|---|
| E3/fixtures/mdfixer-hybrid/ | E3/cases/mdfixer-hybrid/fixture/（main 已搬迁） |
| E3/scripts/run_mdfixer_hybrid.py | E3/cases/mdfixer-hybrid/scripts/run.py（main 已适配） |
| E3/fixtures/mdfixer-target/ | E3/cases/mdfixer-hybrid/target/fixture/ |
| E3/oracle/mdfixer-target.expected.json | E3/cases/mdfixer-hybrid/target/oracle/expected.json |
| E3/patches/mdfixer-target.*.patch | E3/cases/mdfixer-hybrid/target/patches/{reference,invalid}.patch |
| E3/scripts/run_mdfixer_target.py | E3/cases/mdfixer-hybrid/target/scripts/run.py |
| E3/evidence/mdfixer-target/ | E3/cases/mdfixer-hybrid/target/evidence/ |
| E3/HUMAN_REVIEW.md | E3/cases/mdfixer-hybrid/REVIEW.md |
| 旧个人贡献、AI 使用和操作说明 | E3/cases/mdfixer-hybrid/ 下同名文件 |

## 版本、证据和审阅关系

Hybrid 故障源码保持原固定版本 4f13da22499dbee5ad3b63360e5b8b0af1bfcf98，脚本通过 fixed_commit_working_directory 核对旧提交路径。
Target 当前固定提交为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`，提交内路径即当前 target/fixture/。旧 Target 固定版本 b2d5709275471d4264215f6d40bd4bdd3bbfdd8a 继续保存在旧分支；Makefile、C 文件、两个头文件和 .gitignore 与当前版本字节一致，README/SOURCE 只更新说明。
因此从本次新分支克隆，即可通过当前固定提交检查，不依赖另行获取旧 Target 分支。

原 Hybrid 三次证据和原 Target 一次证据逐文件保留原字节；历史命令中的旧路径、时间、执行者和 pending 均是当时记录。
review.json 的 oracle_path 指向当时确认的捕获 input/md-report.json，原 oracle_sha256/observations_sha256 保持有效；current_oracle_path/current_oracle_sha256 分别记录现行输入。
迁移核对 findings、expected_behavior、声明分类及 Patch 字节一致，只适配目录、来源说明和固定版本元数据。个人确认仍指向原记录；2026-10-12 的迁移验证是 Codex 实际执行，不伪填新的人工作业。

请保留当前固定 Fixture 的提交历史，合并使用 Create a merge commit。组级 TARGET 索引由组长在集成时登记，本成员分支仅提交自己的目录。

## 迁移验证结果

- Hybrid：`evidence/20261012T144643089037+0800/`，40/40 PASS，39 条命令。
- Target：`target/evidence/20261012T144600994684+0800/`，44/44 PASS，39 条命令。
- 实际执行者：Codex；新运行不覆盖原日志，不回填新的人工作业。
- 独立完整性核查见 [MIGRATION_VALIDATION.json](MIGRATION_VALIDATION.json)：44 个旧证据文件与迁移前备份逐字节一致，源码与 Patch 内容、Oracle finding/预期相同，当前输入/脚本哈希与实际日志相符，固定提交在新分支历史中可达，所有文件改动限于本成员目录。
