# 本人操作与提交步骤

## 当前完成状态（2026-10-09）

盛浩宇（241250008，lejuwujiang258）已发起个人复现，证据目录为 `evidence/mdfixer-hybrid/20261009T133714630641+0800/`，40/40 PASS。
本人已阅读并明确确认 Codex 辅助核查结论与运行结果一致；贡献、个人确认、README 和 PR 说明已补齐。
个人复现证据提交为 `e9e59b6a017d179ba5e845203c1665ad8450cf37`。源码与证据均已保存为本地提交。
现在可以直接按第 5 步推送分支并创建 PR；第 1 至 4 步保留作通用操作参考，无需重复执行。

## 当前电脑无需重新克隆

B08 仓库已经在：

```text
C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment
```

当前任务分支为 `b08/e3-mdfixer-hybrid`。A08 项目的参考文件及归属已经写入本案例，重跑不需要克隆 A08 仓库。
本机已有 Ubuntu-24.04 WSL、GCC、GNU Make 和 Python；此项无需安装 Docker 或启动 Docker Desktop。
MDFixer HYBRID 分支已经通过 PR #2 合入 `main`，以下命令保留为同类任务的操作参考。

## 1. 阅读与认领

先阅读 E3/README.md、SOURCE.md、参考补丁和本次运行 README。
与 B08 组长确认你负责“HYBRID 混合声明的一套 MDFixer 参考案例”。
在 CONTRIBUTIONS.md 填写实际姓名、学号、GitHub 账号及实际承担内容，注明 AI 辅助。

## 2. 推荐亲自发起一次重跑

打开 PowerShell，执行下面这条命令，把 --operator 的文字换成真实姓名。它会自动启动已有 WSL。

```powershell
wsl -d Ubuntu-24.04 --exec python3 '/mnt/c/Users/26085/Desktop/devops实验课/实验论文/DevOps-Course-Assignment/E3/scripts/run_mdfixer_hybrid.py' --operator '填写姓名（本人发起脚本复现）'
```

末尾应出现：

```text
PASS
ASSERTIONS=40/40
EVIDENCE_DIR=.../E3/evidence/mdfixer-hybrid/新时间目录
```

若实际结果与这里不同，保留新目录的 observations.json 与 commands.txt，记录问题；不要将 FAIL 写成 PASS。
新证据目录中的 operator 来自本次输入；旧 Codex 运行的执行者和 pending 状态保留原样。

## 3. 人工检查与填写审阅

打开刚生成的 README.md 与 observations.json，至少检查：

- 修复前改 4→5 后仍为 10，完整重建为 11。
- 修复后两次仅改头文件分别得到 11、12，日志出现 gcc 重编译。
- 无效候选构建退出码非零，decision 为 REJECTED。
- Makefile 恢复检查通过，恢复后输出 12。
- 源码副本与固定提交一致，仓库故障样例保持原样。

在 HUMAN_REVIEW.md 填写真实审阅日期、姓名、证据目录及结论。
人工审阅和本人发起复现是不同事实；实际做过什么就记录什么。

## 4. 保存自己的确认提交

打开 PowerShell：

```powershell
cd 'C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment'
git status
git add -- E3/CONTRIBUTIONS.md E3/HUMAN_REVIEW.md E3/evidence/mdfixer-hybrid
git commit -m 'docs(e3): record personal review and MDFixer reproduction'
```

CONTRIBUTIONS.md 中的提交 SHA 应填实际值。如本次提交后才取得 SHA，可补入再提交一次。
不要重写旧证据，也不要将编译产物 build/ 或 bin/ 加入 Git。

## 5. 推送并交给组长审查

在同一个目录执行：

```powershell
git push -u origin b08/e3-mdfixer-hybrid
```

然后打开 B08 GitHub 仓库，创建 Pull Request：

- base：main。
- compare：b08/e3-mdfixer-hybrid。
- 建议标题：E3 MDFixer HYBRID 修复基线与真实验证证据。
- 在说明中写明本次仅 HYBRID 案例，DRAFT 及其他声明风格由组里协调。
- 保留 fixture 固定提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`；与组长确认使用保留提交历史的合并方式。

脚本的 oracle 绑定这个固定提交，因此不要 squash/rebase 后丢掉它。若团队必须压缩历史，需要保留可达的基线标签或重新固定输入版本并重新生成证据。
本次没有替你推送、创建 PR 或合并 main。

## 换电脑时

先完成上述推送，再仅克隆 B08 任务分支即可：

```bash
git clone --branch b08/e3-mdfixer-hybrid https://github.com/Delario17/DevOps-Course-Assignment.git
cd DevOps-Course-Assignment
python3 E3/scripts/run_mdfixer_hybrid.py --operator "姓名（本人发起脚本复现）"
```

此处 Python 命令在已有 Linux 工具链的环境中执行。Windows 用户进入 WSL 后执行，不用 Windows 的 MinGW 结果代替 Linux 证据。
