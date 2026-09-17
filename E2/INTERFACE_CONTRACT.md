# A08-B08 接口契约

契约版本：`1.0.0`

## 1. 核心机制

四项服务共享同一种异步 Job 表示。服务受理请求时返回 HTTP 202 和 `job_id`，调用方通过查询端点获取状态与产物引用。每个 Job 包含版本绑定对象 `subject`：

```json
{
  "repository_url": "https://github.com/example/b08-demo.git",
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "configuration_id": "ubuntu-22.04-gcc-11-release"
}
```

三个字段共同标识一次可复现构建。`commit` 使用 40 位完整 SHA；`configuration_id` 描述编译器、操作系统和关键构建选项。产物继续携带 `subject`，消费者在执行前比较版本绑定。

## 2. Job 生命周期

```text
QUEUED -> RUNNING -> SUCCEEDED
                  -> FAILED
                  -> TIMED_OUT
                  -> CANCELLED
```

`SUCCEEDED` 表示分析或修复流程按契约完成。检测出的 `MISSING` 和 `REDUNDANT` 写入 ERROR_REPORT。环境创建失败、任务超时、分析器崩溃和修复候选验证失败写入 `job.error`；失败日志和拒绝报告仍使用完整 ArtifactRef 传递。

创建端点使用 `Idempotency-Key` 请求头，值与请求体中的 `idempotency_key` 相同。同一个键和同一个请求返回同一个 Job；同一个键对应不同请求时返回 HTTP 409 与 `CONTRACT_2001`。

## 3. HTTP 接口

| 操作 | 方法与路径 | 成功响应 |
|---|---|---|
| 生成构建环境 | `POST /v1/dockerfile-jobs` | `202 Accepted` |
| 全量依赖检测 | `POST /v1/full-check-jobs` | `202 Accepted` |
| 增量依赖检测 | `POST /v1/incremental-check-jobs` | `202 Accepted` |
| 修复缺失依赖 | `POST /v1/repair-jobs` | `202 Accepted` |
| 查询任务 | `GET /v1/jobs/{job_id}` | `200 OK` |
| 下载产物 | `GET /v1/artifacts/{artifact_id}/content` | `200 OK` |

创建接口在 `Location` 响应头返回 `/v1/jobs/{job_id}`。完整定义见 `openapi.yaml`。

## 4. DRAFT 契约

DRAFT 输入仓库版本、最多两份构建说明和明确的成功判据：

- `build_command` 判断镜像能否完成构建；
- `verify_command` 判断预期程序能否执行；
- `max_iterations` 和 `timeout_seconds` 限制迭代；
- `base_image_hint` 记录基础镜像偏好。

成功输出包含：

- `DOCKERFILE`；
- `CONTAINER_IMAGE`；
- `BUILD_LOG_BUNDLE`，记录每轮错误、修改和选择理由；
- `build_verification`，保存构建与验证退出码。

下游 A08 在 `environment.container_image` 中传递 DRAFT 生成的完整 `CONTAINER_IMAGE` ArtifactRef，并附带工作目录。服务在执行前比较该 ArtifactRef 与当前请求的 `subject`，从而验证镜像属于同一仓库、commit 和构建配置。

## 5. BuildChecker 与 EChecker 交接

FULL_CHECK 使用 clean build，输出实际依赖图、声明依赖图和 ERROR_REPORT。报告中的每条 finding 含目标、依赖、Makefile位置和执行证据；没有发现 MD/RD 时，ERROR_REPORT 的 `findings` 为空数组，任务仍然成功。

INCREMENTAL_CHECK 额外要求：

- `base_commit`；
- 基线图的 `configuration_id`；
- `ACTUAL_GRAPH` 产物引用；
- 当前提交和增量构建命令。

当前任务的 `configuration_id` 必须等于基线配置。基线图的仓库必须等于当前仓库，图绑定的 commit 必须等于 `base_commit`。输出报告区分新增、消除和保持的发现，并返回可供下一提交使用的更新图。

## 6. MDFixer 契约

REPAIR 入口接受 `ERROR_REPORT` 引用。接收阶段执行以下判定：

1. 报告与请求的仓库地址、commit 和 `configuration_id` 全部一致；
2. findings 非空且每条类型均为 `MISSING`；
3. `makefile_path` 使用相对路径，且不得包含 `..` 或越出当前源码树；
4. 构建、测试和重检命令完整。

修复结果包含 Git Patch、声明风格、修复报告和三项验证结果。候选补丁只有在 build、test、recheck 均为 `PASSED` 时，任务才以 `SUCCEEDED` 结束并设置 `accepted=true`。任一验证失败时，任务以 `FAILED` 结束，错误码为 `REPAIR_6001`，`error.details` 记录拒绝原因及三项候选验证结果。MDFixer 保持原 Makefile 的依赖列表、宏、混合或隐式声明风格。

## 7. 产物协议

Job 响应保存产物元数据，产物正文通过 URI 获取：

```json
{
  "artifact_id": "md-report-full-001",
  "type": "ERROR_REPORT",
  "uri": "artifact://a08-b08/full-001/error-report.json",
  "media_type": "application/json",
  "producer_job_id": "job-full-001",
  "subject": {
    "repository_url": "https://github.com/example/b08-demo.git",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "configuration_id": "ubuntu-22.04-gcc-11-release"
  }
}
```

`artifact://a08-b08/{job}/{path}` 作为不可变逻辑标识，同一 ArtifactRef 中的 `artifact_id` 用于构造 `/v1/artifacts/{artifact_id}/content`。内容响应以 SHA-256 作为 ETag；同一 `artifact_id` 的内容保持不变。

## 8. 错误码

| 错误码 | 含义 | retryable |
|---|---|---:|
| `CONTRACT_2001` | 字段、枚举或幂等约束错误 | false |
| `BASELINE_2002` | 增量基线缺失或版本不匹配 | false |
| `ENV_3001` | 镜像或运行环境不可用 | true |
| `ENV_3002` | 镜像构建失败 | true |
| `EXEC_4001` | 构建命令失败 | false |
| `EXEC_4002` | 任务超时 | true |
| `ANALYSIS_5001` | 检测器执行失败 | true |
| `REPAIR_6001` | 修复候选未通过验证 | false |
| `CANCELLED_7001` | 调用方取消任务 | false |

## 9. 版本演进

兼容变更包括新增可选字段和新增可选产物类型。破坏性变更包括删除字段、字段改名、改变既有字段含义、修改状态语义和让严格消费者无法读取新增字段。

破坏性变更提升主版本号，并由 A08 与 B08 同时更新 Schema、样例、校验器和变更记录。兼容变更提升次版本号。
