# B08 E3：MDFixer HYBRID 基线

## 核心设计

目标规则 `build/main.o: src/main.c $(HEADERS)` 同时包含直接文件项和变量展开项，因此归类为 HYBRID。原 Makefile 的 `HEADERS` 遗漏 `include/config.h`，又额外声明 `include/unused.h`。参考补丁只补充 `config.h`，保留已有 RD，从而单独检验 MD 修复对增量重建的影响。

## 案例产物

| 内容 | 位置 |
|---|---|
| 固定故障项目与 A08 来源 | [`fixture/`](fixture/) |
| MD-only Oracle 与审阅索引 | [`oracle/`](oracle/) |
| 参考修复与失败候选 | [`patches/`](patches/) |
| Linux 行为验证 | [`scripts/run.py`](scripts/run.py) |
| 四次运行证据 | [`evidence/`](evidence/) |
| 贡献、AI 使用与审阅 | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md)、[`AI_USAGE.md`](AI_USAGE.md)、[`REVIEW.md`](REVIEW.md) |

固定样例提交为 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`，提交中的原路径为 `E3/fixtures/mdfixer-hybrid/`，当前路径为 `E3/cases/mdfixer-hybrid/fixture/`。A08 归属见 [`fixture/SOURCE.md`](fixture/SOURCE.md)。

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

盛浩宇于 2026-10-09 发起个人 Linux 复现，40/40 PASS，记录 39 条命令。个人证据位于 [`evidence/20261009T133714630641+0800/`](evidence/20261009T133714630641+0800/)。2026-10-12 的路径回归证据为 [`evidence/20261012T144643089037+0800/`](evidence/20261012T144643089037+0800/)，同样是 40/40 PASS。

## 复现

在 Linux/WSL 的仓库根目录执行：

```bash
python3 E3/cases/mdfixer-hybrid/scripts/run.py \
  --operator "姓名（本人发起复现）"
```

脚本要求 `python3`、`gcc`、`make` 和 `git`，实验在临时副本中完成，新证据写入 `evidence/<时间>/`。
