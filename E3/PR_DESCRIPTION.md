# E3：Hybrid 状态收尾与 MDFixer Target 直接声明基线

新增盛浩宇负责的 Target 直接声明案例。原规则 `build/main.o: src/main.c include/common.h` 漏掉实际读取的 config.h：只改配置值时普通构建仍输出 10，完整重建才输出 11。参考补丁在目标行直接补上 config.h 后，两次仅改头文件均自动重编译，输出 11、12；参考声明与 GCC -MM 项目依赖一致。

交付包括版本固定的 Fixture、MD-only 参考 Oracle、参考与无效 Patch、独立执行脚本、完整 Linux 日志和来源/贡献文档。无效 Patch 在编译前插入 false，强制构建退出码 2，被拒绝后恢复上一份有效 Makefile；精确恢复、重新构建及功能检查通过，输出 12。

同时整理已通过 PR #2 合并的 Hybrid 文档状态：明确已合并和已个人确认，新增绑定原输入及证据哈希的 review.json。原 Hybrid Fixture、Oracle 和三次运行记录保留原字节，历史 pending 由后续审阅记录说明。

验证：Codex 在 Ubuntu 24.04 WSL / GCC 13.3.0 / GNU Make 4.3 / Python 3.12.3 环境实际运行 Target，44/44 项断言通过，39 条命令有 stdout/stderr/退出码；另外核对固定提交、哈希、日志、Patch 快照与 JSON 一致。证据：`E3/evidence/mdfixer-target/20261011T110959885929+0800/`。Target 的成员确认见 E3/HUMAN_REVIEW.md，不将 AI 执行写成本人执行。

固定版本：Target `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`；Hybrid `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`。请保留基线提交历史，确保脚本能够用 git show 校验固定源码。

本 PR 对应“Hybrid 收尾与 Target 声明案例”。两份独立脚本供统一验证入口调用；DRAFT、Macro、Implicit 和最终组级汇总由其余成员按分工完成。本交付为 E3 参考修复实验，不表示真实 MDFixer 服务已实现。
