# B08 E2：需求与接口契约

| 项目 | 内容 |
|---|---|
| 配对编号 | `A08-B08` |
| 作业仓库 | `https://github.com/Delario17/DevOps-Course-Assignment.git` |
| E2 目录 | `E2/` |
| 当前基准提交 | `309237a12aaeb0dba6f03228c0542e3f9385dd9e` |
| 契约状态 | 正式发布前，待 A08 配对评审确认 |

本设计围绕一个问题展开：构建依赖流水线中的每个结果只对特定源码版本和构建配置成立。DRAFT 生成的环境、BuildChecker/EChecker 输出的依赖报告、MDFixer 生成的补丁如果失去版本关系，接口格式即使正确，组合结果也可能无效。

为此，本契约采用“版本绑定的异步任务信封”。`trace_id` 串联一次端到端流程，`subject` 将任务与 `repository_url + commit + configuration_id` 绑定，所有产物引用继续携带同一组信息。MDFixer 接收报告时执行跨文件一致性检查，只处理与当前源码版本一致的 `MISSING` 发现。

## 交付内容

```text
E2/
├── README.md
├── INTERFACE_CONTRACT.md
├── openapi.yaml
├── validate.py
├── requirements.txt
├── BACKLOG.md
├── AI_USAGE.md
├── CONTRIBUTIONS.md
├── CHANGELOG.md
├── contracts/
│   ├── create-request.schema.json
│   ├── task.schema.json
│   ├── artifact.schema.json
│   ├── error-report.schema.json
│   ├── draft-manifest.schema.json
│   └── repair-report.schema.json
├── examples/
│   ├── valid/
│   ├── invalid/
│   ├── errors/
│   └── artifacts/
└── adr/
    ├── 0001-asynchronous-job.md
    └── 0002-version-bound-artifacts.md
```

## 运行验收

从仓库根目录执行：

```bash
python3 -m pip install -r E2/requirements.txt
python3 E2/validate.py
```

校验器检查四类创建请求及其对应响应，并用 Draft 2020-12 JSON Schema 验证有效、无效样例。跨文件检查覆盖仓库、commit、`configuration_id`、基线产物和生产任务的一致性，同时核对每个 `artifact://` URI 对应的本地文件及 SHA-256。

## 产物 URI 与本地样例的对应

`artifact://a08-b08/{job_id}/{path}` 是配对服务之间的不可变逻辑引用。每个 URI 都位于完整 ArtifactRef 中，运行时使用同一引用的 `artifact_id` 请求 `GET /v1/artifacts/{artifact_id}/content`。E2 仓库中保留与样例 URI 对应的静态内容，便于在未部署 API 时复核契约：

| 样例 URI | 本地文件 |
|---|---|
| `artifact://a08-b08/draft-001/Dockerfile` | `E2/examples/artifacts/a08-b08/draft-001/Dockerfile` |
| `artifact://a08-b08/draft-001/iterations.json` | `E2/examples/artifacts/a08-b08/draft-001/iterations.json` |
| `artifact://a08-b08/draft-002/failure.log` | `E2/examples/artifacts/a08-b08/draft-002/failure.log` |
| `artifact://a08-b08/full-c0/actual.json` | `E2/examples/artifacts/a08-b08/full-c0/actual.json` |
| `artifact://a08-b08/full-001/actual.json` | `E2/examples/artifacts/a08-b08/full-001/actual.json` |
| `artifact://a08-b08/full-001/declared.json` | `E2/examples/artifacts/a08-b08/full-001/declared.json` |
| `artifact://a08-b08/full-001/error-report.json` | `E2/examples/artifacts/a08-b08/full-001/error-report.json` |
| `artifact://a08-b08/full-001/redundant-report.json` | `E2/examples/artifacts/a08-b08/full-001/redundant-report.json` |
| `artifact://a08-b08/incremental-001/updated-actual.json` | `E2/examples/artifacts/a08-b08/incremental-001/updated-actual.json` |
| `artifact://a08-b08/incremental-001/error-report.json` | `E2/examples/artifacts/a08-b08/incremental-001/error-report.json` |
| `artifact://a08-b08/repair-001/fix.patch` | `E2/examples/artifacts/a08-b08/repair-001/fix.patch` |
| `artifact://a08-b08/repair-001/report.json` | `E2/examples/artifacts/a08-b08/repair-001/report.json` |
| `artifact://a08-b08/repair-002/report.json` | `E2/examples/artifacts/a08-b08/repair-002/report.json` |

`md-report.artifact.json` 是 `error-report.json` 的 Artifact Record 样例。为了保留初版路径，`md-report.json`、`redundant-report.json`、`draft-manifest.json` 和 `repair-report.json` 作为上表对应文件的同内容镜像，校验器会检查两份内容一致。这些文件用于 E2 契约验收；E3 将使用选定项目的固定 commit 生成运行产物。

## 交接顺序

1. B08 提交 DRAFT 请求，生成 Dockerfile、镜像引用和迭代日志。
2. A08 使用相同 `subject` 执行 FULL_CHECK，生成实际图、声明图和 MD/RD 报告。
3. A08 在后续提交上执行 INCREMENTAL_CHECK，输出更新后的图和发现变化。
4. B08 接收只包含 `MISSING` 发现且版本匹配的报告，运行 REPAIR。
5. 修复候选通过构建、测试和重检后，B08 输出 Git Patch 与修复报告。

## 完成情况

已完成四类异步任务、共享 Job/Artifact/Error Report 模型、OpenAPI 端点、有效与无效样例、ADR 以及自动契约校验。本轮正式提交前修订以基准提交 `309237a` 为起点。

E2 正式提交前尚需 A08 配对评审，并补全成员姓名、学号、实际分工和提交 SHA。下一步是由 A08 在 GitHub Issue 或 PR 中确认端点、字段、错误码和产物读取方式，然后填写 `CONTRIBUTIONS.md` 并将契约标记为正式版本。E2 验收范围是本轮契约交付；真实 DRAFT 项目、固定 commit 和运行报告列入 E3 计划项。

## 提交前填写

`CONTRIBUTIONS.md` 中的成员姓名、学号、实际分工及 A08 评审链接由 B08 成员填写。样例中的 `example/b08-demo` 用于接口验收，E3 选定实际项目后同步替换仓库、commit、镜像与校验命令。
