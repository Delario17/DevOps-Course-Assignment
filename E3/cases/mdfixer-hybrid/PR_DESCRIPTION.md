# E3 MDFixer HYBRID 修复基线

HYBRID 案例的目标规则同时包含直接文件和 `$(HEADERS)` 变量。参考补丁在 `HEADERS` 中补充 `include/config.h`，保留已有 `include/unused.h` RD；修复后两次头文件单独变更均触发重编译，输出依次为 11 和 12。

案例材料位于 `E3/cases/mdfixer-hybrid/`，包含有归属说明的 fixture、MD-only Oracle、两份补丁、Linux 验证脚本和四次运行证据。失败候选退出码为 2，拒绝后恢复有效 Makefile 并输出 12。

盛浩宇（241250008，`lejuwujiang258`）于 2026-10-09 发起个人复现，40/40 PASS，39 条命令已记录；本人已阅读并确认辅助核查结论。
