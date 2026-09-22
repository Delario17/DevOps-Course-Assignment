# ADR-0001：耗时服务采用异步 Job

- 状态：Accepted
- 日期：2026-09-17
- 提议方：B08；确认方：A08-B08 配对评审
- 确认日期：2026-09-20
- 确认依据：A08 评审合并 Commit `5c86f3ff72e12e9dfef3917902836b497e71b671`

## Context

DRAFT 需要多轮镜像构建，BuildChecker执行 clean build，EChecker监控增量构建，MDFixer还要执行构建、测试与重检。这些操作持续时间从数秒到数十分钟，超过普通 HTTP 请求的稳定生命周期。四个服务还需要共享进度、错误与产物引用。

## Decision

创建接口使用 `POST`，成功受理后返回 HTTP 202、`job_id` 和 `Location`。客户端通过 `GET /v1/jobs/{job_id}` 查询状态。状态集合固定为 `QUEUED`、`RUNNING`、`SUCCEEDED`、`FAILED`、`TIMED_OUT`、`CANCELLED`。

请求使用幂等键。相同幂等键和相同请求复用已有 Job；键相同而请求不同返回 `CONTRACT_2001`。

## Alternatives

同步等待的接口实现更短，但客户端连接与构建生命周期耦合，超时后难以判断任务是否仍在运行，也无法稳定传递中间状态。

消息队列直连能够表达异步执行，但会把队列协议暴露给配对组，并增加课堂联调需要部署的基础设施。

## Consequences

服务端保存任务状态和时间戳。调用方可以恢复查询，并通过 `trace_id` 聚合同一次流水线。所有大文件通过 ArtifactRef 返回，Job 响应保持稳定大小。验收样例覆盖受理、成功和失败终态。
