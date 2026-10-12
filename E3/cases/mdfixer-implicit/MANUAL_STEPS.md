# MDFixer IMPLICIT 本人复现步骤

在仓库根目录进入 Linux/WSL，执行：

```bash
python3 E3/cases/mdfixer-implicit/scripts/run.py --operator "孙博一（本人发起复现）"
```

确认末尾显示 `PASS` 和完整断言数，并检查新证据目录中的：

- 修复前增量输出 `10`，干净重建输出 `11`；
- 修复后两次增量输出 `11`、`12`；
- 无效候选退出码非零且决定为 `REJECTED`；
- 回滚后的输出为 `12`。

完成后在 `REVIEW.md` 记录本人运行目录、日期和结论。
