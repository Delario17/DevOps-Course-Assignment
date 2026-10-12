# MDFixer Target：直接声明子案例

负责人：盛浩宇（241250008，lejuwujiang258）。本案例按成员目录安排收拢在 E3/cases/mdfixer-hybrid/target/。

## 故障与验证判据

main.c 实际读取 common.h 和 config.h，初始数值为 6+4=10。原对象规则 `build/main.o: src/main.c include/common.h` 漏掉 config.h。
修复前只把 CONFIG_VALUE 从 4 改为 5，增量构建仍输出 10；相同源码完整重建输出 11。
参考补丁在目标行直接补入 config.h；修复后连续两次只改头文件，不先 clean，分别重编译并输出 11、12。
无效补丁基于参考 Makefile，在编译前插入 false；强制构建退出码 2，被拒绝后恢复上一有效 Makefile 的精确字节，重新构建输出 12。
修复后的 Make 依赖列表与 GCC -MM 项目依赖相等。此案例没有项目内 RD；课件 Target 对应 E2 的 DEPENDENCY_LIST 枚举。

## 材料入口

- [fixture/](fixture/)：当前固定提交 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`；来源见 [SOURCE.md](fixture/SOURCE.md)。
- [oracle/expected.json](oracle/expected.json)：只有 config.h 的 MISSING finding 和上述预期。
- [reference.patch](patches/reference.patch)、[invalid.patch](patches/invalid.patch)：与迁移前字节相同。
- [scripts/run.py](scripts/run.py)：使用新路径，实验和恢复逻辑保持原样。
- [原始 2026-10-11 证据](evidence/20261011T110959885929+0800/README.md)：44/44 PASS、39 条命令，由 Codex 执行，文件内容保留原字节。
- [审阅绑定](oracle/review.json)、[个人审阅](../REVIEW.md)：盛浩宇于 2026-10-11 已阅读并确认原辅助核查结论；迁移后新增 AI 验证另行记录。
- [贡献](../CONTRIBUTIONS.md)、[AI 使用](../AI_USAGE.md)、[提交步骤](../MANUAL_STEPS.md)、[迁移说明](../MIGRATION.md)。

## 仓库根目录执行

```bash
python3 E3/cases/mdfixer-hybrid/target/scripts/run.py --operator "实际执行者"
```

需要 Linux/Ubuntu WSL 的 python3、gcc、make、git，无需 Docker 或 pip 安装。脚本核对固定源码，在临时副本应用补丁，每次建立新 evidence 时间目录，原 Fixture 和旧证据保持不变。

## 新路径实际运行结果

2026-10-12 迁移验证由 Codex 在 Ubuntu 24.04 WSL / GCC 13.3.0 / GNU Make 4.3 / Python 3.12.3 实际执行，44/44 PASS，39 条命令。
[新运行 README](evidence/20261012T144600994684+0800/README.md)、[observations.json](evidence/20261012T144600994684+0800/observations.json)、[commands.txt](evidence/20261012T144600994684+0800/commands.txt)。
固定源码检查、修复后两次不 clean 的增量重建、GCC 与 Make 依赖对照、无效候选拒绝和恢复均通过。旧成员确认与新增 AI 迁移运行分别记录。
