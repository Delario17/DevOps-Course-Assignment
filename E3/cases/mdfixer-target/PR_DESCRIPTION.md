# E3 MDFixer TARGET 独立案例

将 TARGET 直接声明基线收拢到 `E3/cases/mdfixer-target/`。案例包含固定 fixture、MD-only Oracle、参考与失败补丁、Linux 验证脚本、两次实际运行证据和独立个人记录。

参考补丁修复 `build/main.o: src/main.c include/common.h` 遗漏 `include/config.h` 的 MD。修复后两次头文件单独变更均触发重编译，输出依次为 11 和 12；失败候选退出码为 2，拒绝后恢复有效 Makefile 并输出 12。

Linux 验证结果为 44/44 PASS，39 条命令保留标准输出、错误输出和退出码。盛浩宇（241250008，`lejuwujiang258`）已阅读并确认辅助核查结论。
