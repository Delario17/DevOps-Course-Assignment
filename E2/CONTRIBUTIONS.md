# B08 个人贡献与版本追溯记录

## 仓库与基准

| 项目 | 内容 |
|---|---|
| 仓库 | `https://github.com/Delario17/DevOps-Course-Assignment.git` |
| 分支 | `main` |
| E2 初始基准 | `309237a12aaeb0dba6f03228c0542e3f9385dd9e` |
| Git 作者 | `Delario17` |
| 提交日期 | `2026-09-17` |
| 提交说明 | `submit E2` |
| A08 评审记录 | `https://github.com/LoShell/DevOps-Course-Assignment-A08/blob/5c86f3ff72e12e9dfef3917902836b497e71b671/E2/A08_REVIEW.md` |

## 小组信息

本表仅记录 B08 小组的实际工作。
| Git作者 | 学生姓名 |
|---|---|
| Delario17 | 王祎 |
| | |
| | |
| | |

| 姓名 | 学号 | 负责内容 | 关联文件 | 提交 SHA |
|---|---|---|---|---|
|王祎 | 241250007 | DRAFT 请求与构建失败记录 | `draft.request.json`<br>`draft.accepted.json`<br>`draft.failed.json`<br>`failure.log` | f0008a940ebf9de9d775e562518d756e44a46ea7 |
| 盛浩宇 | 241250008 | DRAFT 成功产物与迭代记录 | `draft.succeeded.json`<br>`draft-manifest.schema.json`<br>`Dockerfile`<br>`iterations.json` | f0008a940ebf9de9d775e562518d756e44a46ea7 |
| 朱雨乐 | 241250011 | MDFixer 请求、成功修复与补丁产物 | `repair.request.json`<br>`repair.accepted.json`<br>`repair.succeeded.json`<br>`fix.patch`<br>`report.json` | f0008a940ebf9de9d775e562518d756e44a46ea7 |
| 孙博一 | 241250078 | MDFixer 失败校验、接口文档与自动验收 | `repair.failed.json`<br>`repair-report.schema.json`<br>`openapi.yaml`<br>`validate.py`<br>`INTERFACE_CONTRACT.md` | f0008a940ebf9de9d775e562518d756e44a46ea7 |

`初次创建仓库时一次性上传了所有相关文档，后续会区分提交SHA`

## 已核实的提交

| 日期 | Git 作者 | Commit | 工作内容 | 验证 |
|---|---|---|---|---|
| 2026-09-17 | `Delario17` | `309237a12aaeb0dba6f03228c0542e3f9385dd9e` | 建立 E2 契约初版 | `python3 E2/validate.py` |
| 2026-09-17 | `Delario17` | `f0008a940ebf9de9d775e562518d756e44a46ea7` | 正式提交前契约审查与完整化 | `python3 E2/validate.py` |

本轮 SHA 采用两步留痕：先提交契约修订，取得完整 SHA 后回填本表，再创建一次仅更新贡献记录的提交。

Git 作者字段只记录可核对的仓库元数据。正式提交时，小组信息表应使用真实姓名、学号、实际分工和对应提交 SHA。

小组以四人分工为基准；如实际分工有变化，按提交记录调整“小组信息”表中的职责。

## A08 配对评审

- A08 仓库：`https://github.com/LoShell/DevOps-Course-Assignment-A08`
- 评审链接：`https://github.com/LoShell/DevOps-Course-Assignment-A08/blob/5c86f3ff72e12e9dfef3917902836b497e71b671/E2/A08_REVIEW.md`
- 评审分支最终 Commit：`d8d2d6c23e2fc0d425357722ea23f6c8756c4d87`
- 评审合并 Commit：`5c86f3ff72e12e9dfef3917902836b497e71b671`
- 评审人：刘馨雅、邱莉扉、范从钰、叶原原
- 评审日期：`2026-09-20`
- 评审结论：通过，无必须修改项。A08 接受异步 Job、版本绑定、FULL_CHECK/INCREMENTAL_CHECK 字段、状态与错误语义、ArtifactRef 产物读取方式及增量基线策略。

评审证据索引见 `A08_REVIEW.md`；`BACKLOG.md` 中 `E2-10` 已关闭为 `Done`。
