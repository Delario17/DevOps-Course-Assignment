# B08 E2：需求与接口契约

配对编号：`A08-B08`

本设计围绕一个问题展开：构建依赖流水线中的每个结果只对特定源码版本和构建配置成立。DRAFT 生成的环境、BuildChecker/EChecker 输出的依赖报告、MDFixer 生成的补丁如果失去版本关系，接口格式即使正确，组合结果也可能无效。

为此，本契约采用“版本绑定的异步任务信封”。`trace_id` 串联一次端到端流程，`subject` 将任务与 `repository_url + commit + configuration_id` 绑定，所有产物引用继续携带同一组信息。MDFixer 接收报告时执行跨文件一致性检查，只处理与当前源码版本一致的 `MISSING` 发现。

## 交付内容

```text
lab/
├── README.md
├── INTERFACE_CONTRACT.md
├── openapi.yaml
├── validate.py
├── BACKLOG.md
├── AI_USAGE.md
├── CONTRIBUTIONS.md
├── CHANGELOG.md
├── contracts/
│   ├── create-request.schema.json
│   ├── task.schema.json
│   ├── artifact.schema.json
│   └── error-report.schema.json
├── examples/
│   ├── valid/
│   ├── invalid/
│   └── artifacts/
└── adr/
    ├── 0001-asynchronous-job.md
    └── 0002-version-bound-artifacts.md
```

## 运行验收

```bash
cd lab
python3 validate.py
```

校验器检查：

- 四类创建请求和 B08 的任务响应；
- `job_type=ABC` 被拒绝；
- 增量检测缺少 `baseline` 被拒绝；
- MDFixer 拒绝只包含 RD 的报告；
- 请求、报告与产物的 commit 和 configuration_id 一致；
- 成功任务的产物来源与生产任务一致；
- 失败任务通过 `job.error` 表达，MD/RD 通过报告表达。

## 交接顺序

1. B08 提交 DRAFT 请求，生成 Dockerfile、镜像引用和迭代日志。
2. A08 使用相同 `subject` 执行 FULL_CHECK，生成实际图、声明图和 MD/RD 报告。
3. A08 在后续提交上执行 INCREMENTAL_CHECK，输出更新后的图和发现变化。
4. B08 接收只包含 `MISSING` 发现且版本匹配的报告，运行 REPAIR。
5. 修复候选通过构建、测试和重检后，B08 输出 Git Patch 与修复报告。

## 提交前填写

`CONTRIBUTIONS.md` 中的成员姓名、学号和真实提交 SHA 由 B08 成员填写。样例中的 `example/b08-demo` 用于接口验收，E3 选定实际项目后同步替换仓库、commit、镜像与校验命令。
