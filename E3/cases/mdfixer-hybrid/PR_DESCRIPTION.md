# E3：将盛浩宇的 Hybrid 收尾与 Target 基线迁入成员目录

基于组长目录重组后的 main（d27dc4c），将原 b08/e3-mdfixer-target 的工作收拢至 E3/cases/mdfixer-hybrid/。Target 在该成员目录的 target/ 子案例内，包含直接声明 Fixture、MD-only Oracle、参考/无效 Patch、执行脚本、原始证据与新路径验证。PR 的文件变更仅涉及该成员目录。

Target 修复 `build/main.o: src/main.c include/common.h` 漏掉 config.h 的 MD：修复前只改头文件仍输出旧值 10，完整重建为 11；参考补丁直接补入 config.h 后，连续两次仅改头文件自动重编译，输出 11、12。无效候选构建退出码 2，被拒绝后精确恢复有效 Makefile，重建运行输出 12。Make 依赖与 GCC -MM 项目依赖一致。

迁移前完整文件和 Git 历史已备份，旧任务分支保留。历史 Hybrid 三次证据和 Target 一次证据逐文件保持原字节；个人确认绑定原捕获输入及 observations 哈希，当前 Oracle 单独标明迁移后的路径和版本。既有确认日期及实际执行者不改写。

验证：Codex 在 Ubuntu 24.04 WSL、GCC 13.3.0、GNU Make 4.3、Python 3.12.3 下运行新入口，Hybrid 40/40 PASS，Target 44/44 PASS，各 39 条命令有 stdout/stderr/退出码。新证据分别为 E3/cases/mdfixer-hybrid/evidence/20261012T144643089037+0800/ 与 E3/cases/mdfixer-hybrid/target/evidence/20261012T144600994684+0800/。源码固定版本、输入/脚本/Patch 哈希、命令日志和恢复结果均已检查。

Target 当前固定 Fixture 提交为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`，新分支自身包含此提交，从新分支克隆即可复现。Hybrid 固定提交仍为 4f13da22499dbee5ad3b63360e5b8b0af1bfcf98。请以 Create a merge commit 保留版本历史。

个人贡献、AI 使用、原成员确认、迁移说明与操作步骤均保存在该成员目录。组级 README/贡献索引和其他成员案例保持 main 原样，Target 的组级入口由组长集成时登记。本交付验证已知参考补丁，不表示 MDFixer 自动修复服务已经实现。
