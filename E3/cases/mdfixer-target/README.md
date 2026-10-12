# B08 E3：MDFixer TARGET 基线

## 核心设计

对象规则 `build/main.o: src/main.c include/common.h` 直接列出依赖，因此归类为 TARGET。`main.c` 还读取 `include/config.h`，原规则遗漏该头文件。参考补丁直接把 `config.h` 加入目标行，再通过两次头文件单独变更检查增量重建。

## 案例产物

| 内容 | 位置 |
|---|---|
| 固定故障项目与来源 | [`fixture/`](fixture/) |
| MD-only Oracle | [`oracle/expected.json`](oracle/expected.json) |
| 结构化审阅 | [`oracle/review.json`](oracle/review.json) |
| 参考修复与失败候选 | [`patches/`](patches/) |
| Linux 验证脚本 | [`scripts/run.py`](scripts/run.py) |
| 运行证据 | [`evidence/`](evidence/) |
| 贡献、AI 使用与审阅 | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md)、[`AI_USAGE.md`](AI_USAGE.md)、[`REVIEW.md`](REVIEW.md) |
| 复现与迁移记录 | [`MANUAL_STEPS.md`](MANUAL_STEPS.md)、[`MIGRATION.md`](MIGRATION.md) |

当前 fixture 绑定提交 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`。该提交中的路径为 `E3/cases/mdfixer-hybrid/target/fixture/`；脚本逐文件核对 Makefile、源码和头文件的 Git blob，并用 Oracle 中的 SHA-256 核对迁移后更新路径说明的 README、SOURCE。当前交付路径为 `E3/cases/mdfixer-target/fixture/`。

## 验证结果

| 阶段 | 实际结果 |
|---|---|
| 初始完整构建 | 10 |
| 修复前 `CONFIG_VALUE` 4→5，增量构建 | 保持 10 |
| 相同源码完整重建 | 11 |
| 修复后 4→5，增量构建 | 重编译并输出 11 |
| 修复后 5→6，增量构建 | 再次重编译并输出 12 |
| 失败候选 | 退出码 2，REJECTED |
| 恢复有效 Makefile | 字节一致，输出 12 |

2026-10-11 和 2026-10-12 的 Linux 验证均为 44/44 PASS，每次记录 39 条命令。盛浩宇于 2026-10-11 阅读并确认辅助核查结论，实验执行者为 Codex，具体见 [`REVIEW.md`](REVIEW.md)。

## 复现

在 Linux/WSL 的仓库根目录执行：

```bash
python3 E3/cases/mdfixer-target/scripts/run.py --operator "实际执行者"
```

脚本要求 `python3`、`gcc`、`make` 和 `git`，实验在临时副本中完成，新证据写入 `evidence/<时间>/`。
