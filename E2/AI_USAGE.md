# AI 使用记录

## 2026-09-17：E2 契约设计

| 项目 | 记录 |
|---|---|
| 工具/模型 | Codex，本次课程作业对话 |
| 任务 | 阅读四篇论文与 E2 课件，为 B08 设计 DRAFT/MDFixer 及四服务公共契约 |
| 提示摘要 | B08 小组需要把 E2 作业放入当前目录的 `lab` 目录 |
| AI 建议 | 使用异步 Job、统一状态、类型化 ArtifactRef、完整 commit 与 configuration_id 绑定、REPAIR 只消费 MD |
| 人工采纳 | 采纳异步 Job 和版本绑定机制；端点沿用课件参考命名；增加产物下载端点解决 `artifact://` 读取问题 |
| 人工修改 | 将状态名固定为课件中的 `QUEUED/RUNNING/SUCCEEDED` 等；将补丁接受条件收敛为 build、test、recheck 全部通过 |
| 拒绝内容 | 未采用把完整构建日志内嵌到 Job 响应的方案；日志改为 `BUILD_LOG_BUNDLE` 引用 |
| 关联文件 | `INTERFACE_CONTRACT.md`、`openapi.yaml`、`contracts/`、`examples/`、`adr/` |
| 验证 | 运行 `python3 E2/validate.py`；6 份 Schema、4 类请求、8 份 Job 响应、3 份 HTTP 错误样例与 13 份可读取产物通过，8 种逻辑错误被拒绝 |

## 使用原则

AI 参与需求提炼、Schema起草、样例生成和一致性检查。B08 成员负责确认配对接口、替换真实实验项目参数、执行 E3 构建与检测，并以 Git 提交记录个人贡献。

## 2026-09-17：正式提交前审查

| 项目 | 记录 |
|---|---|
| 工具/模型 | Codex，本次课程作业对话 |
| 任务 | 根据 E2 课件重新检查仓库追溯、OpenAPI 端点、JSON Schema、失败响应、产物读取和配对评审状态 |
| 提示摘要 | 在保留成员姓名和学号占位的前提下，直接修正正式提交前的阻塞项并完成验证 |
| AI 建议 | 端点分别限定 `job_type`；空检测报告与 MDFixer 的 MD-only 输入分层约束；补齐 HTTP 错误响应、成功响应和失败候选样例；使用 JSON Schema 执行实际校验 |
| 处理决定 | 采纳上述契约完整性修订；同时修正 `E2/` 路径、记录实际仓库与基准提交，并建立产物 URI 到本地样例的映射 |
| 完成情况 | B08 成员姓名、学号、分工和提交 SHA 已回填；A08 配对评审已于 2026-09-20 完成 |
| 版本状态 | A08 评审结论为通过且无必须修改项；契约标记为 `1.0.0` |
| 验证 | `python3 E2/validate.py`；同时核对 OpenAPI 外部引用、`artifact://` 本地映射与 SHA-256 |

## 2026-09-22：A08 配对评审收口

| 项目 | 记录 |
|---|---|
| 工具/模型 | Codex，本次课程作业对话 |
| 任务 | 核对 A08 仓库的评审文档、分支历史和合并 Commit，在 B08 仓库回填评审证据 |
| 证据 | A08 仓库 `LoShell/DevOps-Course-Assignment-A08`；评审分支 Commit `d8d2d6c`；合并 Commit `5c86f3f` |
| 处理决定 | 根据 A08 “通过，无必须修改项”的结论，关闭 E2-10，接受两项 ADR，发布契约 `1.0.0` |
| 关联文件 | `A08_REVIEW.md`、`CONTRIBUTIONS.md`、`BACKLOG.md`、`CHANGELOG.md`、`adr/` |
| 验证 | 对照 A08 固定 Commit 中的总评审、FULL_CHECK/INCREMENTAL_CHECK 详细评审和配对沟通记录 |
