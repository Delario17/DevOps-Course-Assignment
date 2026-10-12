# MDFixer HYBRID 复现步骤

在 Linux/WSL 的仓库根目录执行：

```bash
python3 E3/cases/mdfixer-hybrid/scripts/run.py \
  --operator "姓名（本人发起复现）"
```

成功运行输出 `PASS`、`ASSERTIONS=40/40` 和新建的 `EVIDENCE_DIR`。核对修复前增量旧值、完整重建新值、修复后两次增量重编译、失败候选拒绝和 Makefile 字节恢复。

个人复现与审阅更新仅修改本案例的 `CONTRIBUTIONS.md`、`REVIEW.md` 和新证据目录。
