# 盛浩宇本人操作与提交

## 当前状态（2026-10-11）

原 Hybrid 已通过 PR #2 合并 main，个人复现与确认仍有效。本次已在最新 main 的基础上建立 `b08/e3-mdfixer-target`，完成 Hybrid 状态文档收尾和 Target 新案例，Linux 结果 44/44 PASS。
Target 本次由 Codex 执行；个人阅读确认与实际执行分别记录于 HUMAN_REVIEW.md。新分支目前保存在本地，尚未推送或创建本次 PR。

## 无需再克隆或安装

本机已有 B08 仓库：

```text
C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment
```

Ubuntu-24.04 WSL、GCC、GNU Make、Python 已可用；此案例无需 Docker。重跑不需要再克隆 A08，源码归属已记录。

## 可选：本人发起 Target 复现

如果需要增加本人执行证据，在 PowerShell 执行：

```powershell
wsl -d Ubuntu-24.04 --exec python3 '/mnt/c/Users/26085/Desktop/devops实验课/实验论文/DevOps-Course-Assignment/E3/scripts/run_mdfixer_target.py' --operator '盛浩宇（本人发起 Target 脚本复现）'
```

预期末尾为 PASS、ASSERTIONS=44/44、EVIDENCE_DIR=新目录。每次创建新证据，不影响旧目录。
可把新目录告诉 Codex 协助核查，再将实际复现事实补到 CONTRIBUTIONS.md 与 HUMAN_REVIEW.md；未执行时保留 Codex 为本次执行者。

## 阅读与确认

阅读 TARGET_README.md、此次运行 README、observations.json 和两个 Patch。核对修复前增量 10/完整重建 11、修复后两次增量 11/12、失败退出码 2、拒绝及恢复成功。
确认时在 HUMAN_REVIEW.md 和 oracle/mdfixer-target.review.json 记录真实确认日期、本人身份及证据目录。原始证据的 pending 是执行时状态，保留原样。
单独阅读并确认结论可以记为辅助审阅，不等于本人执行脚本。

## 推送及创建 PR

在 PowerShell 执行：

```powershell
cd 'C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment'
git status
git push -u origin b08/e3-mdfixer-target
```

在 GitHub 创建 PR，base 为 main，compare 为 b08/e3-mdfixer-target。标题和完整正文见 PR_DESCRIPTION.md，可直接复制；交给组长审阅。
若另有本人新增证据或确认内容未提交，先只把相关新目录和修改文档 git add/commit，再推送。
保留 Fixture 固定提交历史：Target 的 b2d5709275471d4264215f6d40bd4bdd3bbfdd8a 和 Hybrid 的 4f13da22499dbee5ad3b63360e5b8b0af1bfcf98 均需可达。使用 GitHub Create a merge commit 可保留；如改用压缩合并，应先保留基线标签或重新绑定并生成证据。

## 给组长的简短说明

我按新分工补完了 Hybrid 的状态文档，并新增 Target 直接声明案例，包含 Fixture、固定 Oracle、参考/无效 Patch 和 Linux 验证日志。Target 44/44 检查通过：修复前只改头文件不重建，补齐后连续两次自动重编译；失败候选能够拒绝并恢复。原 Hybrid 证据保留。分支是 b08/e3-mdfixer-target，材料入口在 E3/README.md，两个独立脚本可接入统一验证入口。代码和文档由 Codex 辅助准备，本次 Target 运行由 Codex 执行。
