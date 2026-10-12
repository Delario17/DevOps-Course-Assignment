# Target 直接声明案例来源与目录迁移

- 负责人：盛浩宇（241250008，lejuwujiang258）。
- C 源码和 common.h/config.h 最初来源于 A08：https://github.com/LoShell/DevOps-Course-Assignment-A08，参考版本 `f8584a58e7be9d39ca630b5c6617a9ed25e8e4da` 的 `E3/fixtures/md-rd/`。
- B08 原 Target 固定版本：`b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`，原路径 `E3/fixtures/mdfixer-target/`。旧分支 `b08/e3-mdfixer-target` 及本地备份保留该版本。
- 2026-10-12 的固定版本提交为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`，提交中路径为 `E3/cases/mdfixer-hybrid/target/fixture/`。
- 当前交付路径为 `E3/cases/mdfixer-target/fixture/`。Makefile、C 源码、两个头文件和 `.gitignore` 与固定版本字节一致。
- 对象目标依赖为直接文件名：`build/main.o: src/main.c include/common.h`。不使用 HEADERS/DEPS 依赖变量，不声明 unused.h，仅构造 config.h 的 MD，没有项目内 RD。
- 参考修复直接在该目标行添加 include/config.h。CC/CPPFLAGS/CFLAGS 用于编译命令，不改变直接声明分类。
- 材料与脚本由 Codex 辅助准备；实际执行和个人确认分别记录。

初始输出 10。修复前 CONFIG_VALUE 4→5 的普通构建仍输出 10，完整重建输出 11。
修复后两次只改头文件应依次输出 11、12；失败候选应被拒绝，恢复上一份有效 Makefile 后构建和运行通过。
