# MDFixer HYBRID 复现步骤

## 环境与入口

实验脚本使用 Linux 工具链，需要 `python3`、`gcc`、`make` 和 `git`。在 Linux 或 WSL 中从仓库根目录执行：

```bash
python3 E3/cases/mdfixer-hybrid/scripts/run.py \
  --operator "姓名（本人发起复现）"
```

Windows PowerShell 可直接调用 WSL：

```powershell
wsl -d Ubuntu-24.04 --exec python3 '/mnt/c/仓库路径/DevOps-Course-Assignment/E3/cases/mdfixer-hybrid/scripts/run.py' --operator '姓名（本人发起复现）'
```

成功运行的终端末尾为：

```text
PASS
ASSERTIONS=40/40
EVIDENCE_DIR=.../E3/cases/mdfixer-hybrid/evidence/<时间目录>
```

## 证据核对

打开新证据目录中的 `README.md`、`observations.json` 和 `commands.txt`，核对以下行为：

- 修复前 `CONFIG_VALUE` 从 4 改为 5 后，增量构建仍输出 10，完整重建输出 11。
- 参考修复后，两次头文件单独变更分别输出 11 和 12，构建日志包含 GCC 重编译。
- 无效候选构建以非零状态退出，`decision` 为 `REJECTED`。
- 恢复后 Makefile 字节一致，重新构建输出 12。
- fixture 与固定提交一致，仓库中的故障样例保持不变。

核对结果写入 [`REVIEW.md`](REVIEW.md)，个人实际贡献写入 [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md)。

## 提交案例

每个成员只暂存本案例目录：

```bash
git add -- E3/cases/mdfixer-hybrid
git commit -m 'test(e3): record MDFixer hybrid reproduction'
```

案例合入集成分支后，由集成负责人更新 `E3/README.md`、`E3/CONTRIBUTIONS.md` 和 `E3/AI_USAGE.md`。
