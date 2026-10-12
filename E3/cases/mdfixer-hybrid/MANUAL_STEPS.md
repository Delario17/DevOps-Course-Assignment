# 新目录版本的提交步骤（2026-10-12）

本次已基于最新 main 的目录重组建立新分支 b08/e3-mdfixer-hybrid-layout。全部工作保存在 E3/cases/mdfixer-hybrid/，Target 是其中的 target/ 子案例。
材料、个人记录和新路径验证已齐全并提交到本地。Hybrid 40/40 PASS，Target 44/44 PASS，原个人确认保留，不需要重新填写身份、重跑实验或再次 git add/commit。

## 旧材料已备份

本机备份目录：

```text
C:\Users\26085\Desktop\devops实验课\实验论文\backups\mdfixer-before-layout-20261012-7e53650
```

旧分支 b08/e3-mdfixer-target 仍保留，文件 ZIP 和完整 Git bundle 均已保存。迁移关系见 MIGRATION.md。

## 1. 推送新分支

打开 PowerShell，依次执行：

```powershell
cd 'C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment'
git switch b08/e3-mdfixer-hybrid-layout
git push -u origin b08/e3-mdfixer-hybrid-layout
```

如提示 GitHub 登录，使用自己的账号登录。推送新分支不会直接合并 main。

## 2. 创建新的 PR

推送成功后打开 [新 PR 页面](https://github.com/Delario17/DevOps-Course-Assignment/compare/main...b08/e3-mdfixer-hybrid-layout?expand=1)。

1. base 选择 main，compare 选择 b08/e3-mdfixer-hybrid-layout。
2. 标题填写：`E3：将盛浩宇的 Hybrid 收尾与 Target 基线迁入成员目录`。
3. 打开本目录 PR_DESCRIPTION.md，把第一行标题之后的全部文字复制到 Description。
4. 在 Files changed 检查所有文件均在 E3/cases/mdfixer-hybrid/ 下。
5. 点击 Create pull request，将新 PR 链接发给组长。

如果原 b08/e3-mdfixer-target 的 PR 仍未合并，请告诉组长该旧 PR 已由新目录版本替代；保留旧分支和备份便于溯源。
合并时请使用 Create a merge commit，保留当前固定 Fixture 提交；不要自己直接合并 main。
组级 Target 索引由组长集成时登记，本分支只更新自己的成员目录。

## 可选：今后复现新入口

在已有 Linux/WSL 工具链的仓库根目录运行：

```bash
python3 E3/cases/mdfixer-hybrid/scripts/run.py --operator "真实执行者"
python3 E3/cases/mdfixer-hybrid/target/scripts/run.py --operator "真实执行者"
```

每次创建新 evidence 时间目录，旧证据不覆盖。当前提交已有新的真实 Linux 验证证据，此重跑不作为提交前必做项。
