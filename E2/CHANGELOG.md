# 接口变更记录

## 1.0.0 - 2026-09-17

- 定义 DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 四类异步任务。
- 固定六种任务状态和 output/error 互斥规则。
- 引入 `subject`，绑定仓库、完整 commit 与构建配置。
- 定义 ArtifactRef、ERROR_REPORT 和 MDFixer 的 MD-only 约束。
- 增加四个创建端点、任务查询端点和产物下载端点。
- 提供有效与无效样例及自动校验脚本。
