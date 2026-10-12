# MDFixer TARGET 复现步骤

在 Linux/WSL 的仓库根目录执行：

```bash
python3 E3/cases/mdfixer-target/scripts/run.py \
  --operator "姓名（本人发起复现）"
```

成功运行输出 `PASS`、`ASSERTIONS=44/44` 和新建的 `EVIDENCE_DIR`。核对新证据中的以下结果：

- 修复前增量输出 10，完整重建输出 11。
- 修复后两次增量输出 11 和 12，均出现编译命令。
- 直接声明的 Make 依赖集与 GCC 头文件依赖集相等。
- 失败候选退出码非零，恢复后输出 12。

个人复现与审阅更新仅修改本案例的 `CONTRIBUTIONS.md`、`REVIEW.md` 和新证据目录。
