# Target 直接声明案例来源与范围

- 负责人：盛浩宇（241250008，lejuwujiang258）。
- 基于 B08 已合并的 HYBRID 案例，合并版本为 `59f45051ca7904247198b3aba6800b6f194333eb`。
- C 源码和 common.h/config.h 最初来源于 A08：https://github.com/LoShell/DevOps-Course-Assignment-A08，参考版本 `f8584a58e7be9d39ca630b5c6617a9ed25e8e4da` 的 `E3/fixtures/md-rd/`。
- 本案例将对象目标的依赖列表改为直接文件名：`build/main.o: src/main.c include/common.h`。
- 不使用 HEADERS/DEPS 等依赖变量，也不声明 unused.h；仅构造 include/config.h 的 MD，没有项目内 RD。
- 参考修复直接在上述目标行添加 include/config.h。
- 规则中的 CC、CPPFLAGS、CFLAGS 仅用于编译命令，不改变直接声明分类。
- 材料与脚本由 Codex 辅助准备，实际执行与成员确认分别记录。

初始输出为 10。修复前 CONFIG_VALUE 从 4 改为 5 时，普通构建仍输出 10，完整重建输出 11。
修复后两次只改头文件应分别输出 11、12；失败候选应被拒绝，恢复上一个有效 Makefile 后构建和运行通过。
