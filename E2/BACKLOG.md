# A08-B08 Backlog

| ID | 任务 | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|---|
| E2-01 | 统一异步任务模型 | A08/B08 | `contracts/task.schema.json` | 四种 job_type、六种状态、output/error互斥关系可表达 | Done |
| E2-02 | 创建请求模型 | A08/B08 | `contracts/create-request.schema.json` | 四类请求均通过校验 | Done |
| E2-03 | DRAFT 契约 | B08 | DRAFT 请求、受理、成功和失败样例 | 构建命令、验证命令、迭代限制与三类产物齐全 | Done |
| E2-04 | MDFixer 契约 | B08 | REPAIR 请求、受理、成功与失败样例 | 只消费 MD，补丁经过 build/test/recheck，失败候选保留拒绝原因 | Done |
| E2-05 | 检测报告交接 | A08/B08 | `error-report.schema.json` 与样例 | 目标、依赖、位置、证据和版本绑定完整 | Done |
| E2-06 | 产物访问协议 | A08/B08 | `artifact.schema.json`、下载端点与可读取产物样例 | URI 可解析到本地样例，ArtifactRef 与文件 SHA-256 一致 | Done |
| E2-07 | 自动契约检查 | B08 | `validate.py` | Schema、OpenAPI、有效样例和产物映射通过，8 种逻辑错误被拒绝 | Done |
| E2-08 | 异步方案决策 | B08 | ADR-0001 | 记录背景、选择、替代方案和影响 | Done |
| E2-09 | 版本绑定决策 | B08 | ADR-0002 | 明确 commit、配置和产物一致性规则 | Done |
| E2-10 | 配对评审 | A08/B08 | GitHub Issue/PR 评审记录与契约版本 | A08 对端点、字段、错误码和读取方式确认；下一步：B08 发起 Issue/PR，A08 留下结论后回填 `CONTRIBUTIONS.md` | Review（待 A08 确认） |
| E3-01 | 选择 DRAFT 实验项目 | B08 | 真实仓库、完整 SHA、构建和验证命令 | 原始项目可在目标环境复现构建 | Planned |
| E3-02 | 固定 MD 报告 | A08/B08 | 绑定真实提交的 ERROR_REPORT | 报告至少包含一个可复现 MD | Planned |
| E3-03 | 运行端到端闭环 | A08/B08 | DRAFT→检测→修复→重检证据 | trace_id 串联全部 Job，补丁重检通过 | Planned |
