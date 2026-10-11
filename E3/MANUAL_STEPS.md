# 盛浩宇本人操作与提交

## 当前状态（2026-10-11）

原 Hybrid 已通过 PR #2 合并 main，个人复现与确认仍有效。本次已在最新 main 的基础上建立 `b08/e3-mdfixer-target`，完成 Hybrid 状态文档收尾和 Target 新案例，Linux 结果 44/44 PASS。
Target 本次由 Codex 执行；盛浩宇已阅读并明确确认辅助核查结论，记录于 HUMAN_REVIEW.md 与 oracle/mdfixer-target.review.json。
代码、证据、身份、贡献、AI 使用、审阅日期和 PR 描述均已补齐并保存为本地提交。当前无需手工补写文档、重新实验或再次 git add/commit；下一步是推送分支并创建 PR。新分支尚未推送或创建本次 PR。

## 无需再克隆或安装

本机已有 B08 仓库：

```text
C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment
```

Ubuntu-24.04 WSL、GCC、GNU Make、Python 已可用；此案例无需 Docker。重跑不需要再克隆 A08，源码归属已记录。

## 提交前已核对

| 项目 | 状态 |
|---|---|
| 盛浩宇姓名、学号、GitHub 账号 | 已填写 |
| Hybrid 已合并及已确认状态 | 已整理 |
| Target Fixture、Oracle、参考/无效 Patch | 齐全，绑定实际固定提交 |
| Linux 构建、增量重编译、拒绝与恢复证据 | 44/44 PASS，39 条命令 |
| 本次 Target 成员阅读确认 | 已记录，2026-10-11 |
| 来源、个人贡献、AI 使用和实际提交 SHA | 已填写 |
| PR 标题和正文 | 已写好，见 PR_DESCRIPTION.md |

原始 Oracle 和运行记录中的 PENDING_HUMAN_REVIEW 是准备/执行时快照，不是需要填写的空白。后续完成的当前确认记录见 HUMAN_REVIEW.md 与 review.json。

## 1. 推送已经提交好的分支

打开 PowerShell，依次执行：

```powershell
cd 'C:\Users\26085\Desktop\devops实验课\实验论文\DevOps-Course-Assignment'
git switch b08/e3-mdfixer-target
git push -u origin b08/e3-mdfixer-target
```

推送时如果要求 GitHub 登录，使用自己的 GitHub 账号完成。此命令将本地分支和所有提交上传，不直接合并 main。

## 2. 在 GitHub 创建 PR

推送成功后打开 [本次 PR 比较页面](https://github.com/Delario17/DevOps-Course-Assignment/compare/main...b08/e3-mdfixer-target?expand=1)。

1. 检查 base 为 `main`，compare 为 `b08/e3-mdfixer-target`。
2. 标题填：`E3：Hybrid 状态收尾与 MDFixer Target 直接声明基线`。
3. 打开本地 `E3/PR_DESCRIPTION.md`，复制第一行标题以后的全部内容到 Description。
4. 点击 `Create pull request`，把生成的 PR 链接交给组长审查。

GitHub 操作依据：[官方创建 PR 说明](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)。
请组长在合并时保留 Fixture 固定提交历史：Target 的 b2d5709275471d4264215f6d40bd4bdd3bbfdd8a 和 Hybrid 的 4f13da22499dbee5ad3b63360e5b8b0af1bfcf98 均需可达。GitHub 的 Create a merge commit 可保留；如改用压缩合并，应先保留基线标签或重新绑定并生成证据。

## 可选：以后增加本人执行证据

如果需要增加本人执行证据，在 PowerShell 执行：

```powershell
wsl -d Ubuntu-24.04 --exec python3 '/mnt/c/Users/26085/Desktop/devops实验课/实验论文/DevOps-Course-Assignment/E3/scripts/run_mdfixer_target.py' --operator '盛浩宇（本人发起 Target 脚本复现）'
```

预期末尾为 PASS、ASSERTIONS=44/44、EVIDENCE_DIR=新目录。每次创建新证据，不影响旧目录。
可把新目录告诉 Codex 协助核查，再将实际复现事实补到 CONTRIBUTIONS.md 与 HUMAN_REVIEW.md；未执行时保留 Codex 为本次执行者。

新增复现材料属于后续独立补充；若新增，核对后提交该新目录和相应说明，再推送同一分支即可更新 PR。当前已有材料可以提交审查，无需先完成此可选重跑。

## 给组长的简短说明

我按新分工补完了 Hybrid 的状态文档，并新增 Target 直接声明案例，包含 Fixture、固定 Oracle、参考/无效 Patch 和 Linux 验证日志。Target 44/44 检查通过：修复前只改头文件不重建，补齐后连续两次自动重编译；失败候选能够拒绝并恢复。原 Hybrid 证据保留。分支是 b08/e3-mdfixer-target，材料入口在 E3/README.md，两个独立脚本可接入统一验证入口。代码和文档由 Codex 辅助准备，本次 Target 运行由 Codex 执行。
