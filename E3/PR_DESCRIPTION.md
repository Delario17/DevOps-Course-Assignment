# E3 MDFixer HYBRID 修复基线与真实验证证据

新增一套 B08 混合声明风格的 MDFixer 测试基线。项目实际读取 config.h，但 HEADERS 漏写该文件；修复前仅修改配置值，普通构建仍输出旧值 10，完整重建输出 11。参考补丁补上 config.h 后，两次只改头文件均自动重新编译，输出依次为 11、12。

材料包含注明 A08 归属的故障项目、固定 MD-only 参考输入、参考补丁、故意失败的候选、验证与恢复脚本、实际日志和个人操作说明。失败候选构建退出码为 2，被拒绝后恢复候选应用前的有效 Makefile，重新构建运行输出 12。

验证：Codex 在 Ubuntu 24.04 WSL、GCC 13.3.0、GNU Make 4.3、Python 3.12.3 环境执行最终脚本，40/40 项断言通过。固定样例提交为 4f13da22499dbee5ad3b63360e5b8b0af1bfcf98，最终证据目录为 E3/evidence/mdfixer-hybrid/20261009T123645645063+0800/。请保留该基线提交历史。

个人复现：盛浩宇（241250008，lejuwujiang258）于 2026-10-09 本人发起脚本，40/40 PASS，39 条命令已记录。个人证据为 E3/evidence/mdfixer-hybrid/20261009T133714630641+0800/；详细文件核查由 Codex 辅助完成，README、命令、JSON、补丁和哈希一致，本人已阅读并确认结论与运行结果一致。

本次仅交付 HYBRID 案例，原有 unused.h RD 保留。DRAFT、其他声明风格和实际 MDFixer 服务由后续任务负责。成员身份、个人复现和本人确认已记录于 E3/CONTRIBUTIONS.md 与 E3/HUMAN_REVIEW.md；AI 执行与人工确认分别记录。
