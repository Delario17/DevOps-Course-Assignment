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
| 验证 | 运行 `python3 validate.py`；有效样例通过，无效 job_type、缺失 baseline 和 RD 修复请求被拒绝 |

## 使用原则

AI 参与需求提炼、Schema起草、样例生成和一致性检查。B08 成员负责确认配对接口、替换真实实验项目参数、执行 E3 构建与检测，并以 Git 提交记录个人贡献。
