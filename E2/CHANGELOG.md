# 接口变更记录

## Unreleased（目标版本 `1.0.0`）- 2026-09-17

基准提交 `309237a12aaeb0dba6f03228c0542e3f9385dd9e` 属于未发布草案。本轮将契约收口为首个正式版本 `1.0.0`，A08 配对评审完成后发布。

- 将作业路径从 `lab/` 更正为仓库内的 `E2/`，补充仓库地址和基准提交。
- 将检测和修复请求中的字符串 `environment.image_ref` 替换为带版本绑定的 `environment.container_image` ArtifactRef。
- 对四个创建端点的 `job_type` 、成功状态语义、增量基线与版本绑定执行更严格的契约检查。
- 区分“检查成功且无发现”与 MDFixer 必须消费 `MISSING` 发现的约束。
- 补充 FULL_CHECK、INCREMENTAL_CHECK、HTTP 错误和 REPAIR 候选失败等样例，并将样例纳入 Draft 2020-12 JSON Schema 校验。
- 记录产物 URI 与本地样例的映射、个人贡献占位项和 A08 评审的待办步骤。

## 未发布草案（`309237a`）- 2026-09-17

- 定义 DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 四类异步任务。
- 固定六种任务状态和 output/error 互斥规则。
- 引入 `subject`，绑定仓库、完整 commit 与构建配置。
- 定义 ArtifactRef、ERROR_REPORT 和 MDFixer 的 MD-only 约束。
- 增加四个创建端点、任务查询端点和产物下载端点。
- 提供有效与无效样例及自动校验脚本。
