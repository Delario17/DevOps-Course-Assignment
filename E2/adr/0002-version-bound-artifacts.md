# ADR-0002：任务与产物绑定源码版本和构建配置

- 状态：Proposed（B08 已采纳，待 A08 配对评审确认）
- 日期：2026-09-17
- 提议方：B08；确认方：A08-B08 配对评审

## Context

依赖图、错误报告和修复补丁均受源码版本及构建配置影响。相同仓库在不同 commit、编译器选项或平台下会产生不同实际依赖。仅传文件地址无法阻止下游把旧报告用于新源码。

## Decision

每个请求包含 `subject`，由 `repository_url`、40位 `commit` 和 `configuration_id` 组成。每个 ArtifactRef 重复记录生产时的 `subject` 和 `producer_job_id`。

消费者执行前进行相等性检查：

- FULL_CHECK、INCREMENTAL_CHECK 和 REPAIR 的 `environment.container_image` 携带 DRAFT 产出的完整 ArtifactRef，其 subject 等于当前请求 subject；
- INCREMENTAL_CHECK 的历史图仓库等于当前仓库，commit 等于 `base_commit`，配置等于当前配置；
- REPAIR 的 ERROR_REPORT subject 等于修复请求 subject；
- Job 输出产物的 subject 等于 Job 输入 subject，`producer_job_id` 等于当前 `job_id`。

## Alternatives

只依赖文件名或目录名表达版本时，重命名、覆盖和缓存会破坏对应关系。只记录 commit 时，Debug/Release、编译器版本和可选特性仍会混用。

## Consequences

接口中存在少量重复元数据，换来可追溯的跨服务校验。版本不匹配在任务创建阶段返回 `BASELINE_2002` 或 `CONTRACT_2001`。`validate.py` 对样例执行同样的跨文件检查。
