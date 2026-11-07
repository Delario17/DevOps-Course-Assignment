# E7-B 完整验证与个人边界测试报告（241250078 孙博一）

## 1. 基本信息

- 小组/轨道：B08 / B（DRAFT）
- 姓名/学号：孙博一 / 241250078
- 实验日期：2026-11-07（Asia/Shanghai）
- 仓库：`https://github.com/Delario17/DevOps-Course-Assignment`
- 服务器目录：`/root/241250078/B08-remote-repo/E6`
- E7 基线（已合并 E6 的最新 main）：`15b6e87ae17875abe504fda1dc8e55316124eb95`
- 本人 E7 测试提交：`63e2e1160e6bc682dace874f0e1adb2f21027f5e`
- 分支：`student/241250078/e5-e7`

## 2. 本人新增边界测试

新增 `services/draft/tests/test_student_241250078_e7.py`。E6 已覆盖 `/bin/sh: 1: make: not found`，本测试增加另一种常见 shell 文本：

```text
/bin/sh: 1: make: command not found
```

预期 `classify_failure` 同样返回 `MISSING_MAKE`。该测试取自 E7 手册给出的边界方向，并补充了具体 shell 前缀和学生专属测试文件；它与本人 E6 的“必需 Dockerfile 指令顺序不可改变”测试不重复。

定向测试结果：`1 passed`，退出码 0，证据位于 `work/e7-241250078-targeted/`。

## 3. 重新构建与完整单元测试

执行：

```bash
python3 scripts/course.py build \
  --out work/e7-241250078-build --build-timeout 1200
```

- 构建退出码：0
- 完整单元测试：`28 passed in 0.25s`
- 服务镜像：`course1027-draft:241250078`
- 服务镜像 ID：`sha256:cb70dc6240cc611c4836aa496bea328a5543cafdc258603dd788353794fabe84`

## 4. 完整 Gate

执行：

```bash
python3 scripts/course.py gate --replay \
  --out work/e7-241250078-gate --build-timeout 1200
```

整体退出码为 0，`gate-result.json` 的 `passed=true`，六项检查结果如下：

| 场景 | case.passed | 工作流状态/退出码 | 验收含义 |
|---|---:|---|---|
| unit-tests | true | 退出 0 | 镜像内 28 项测试全部通过 |
| success | true | SUCCEEDED / 0 | 两轮构建成功，同一 image ID 禁网运行并输出 `hello E3` |
| wrong-output | true | FAILED / 1 | 实际输出仍为 `hello E3`，与故意错误的期望不匹配，正确拒绝 |
| invalid-candidate | true | FAILED / 1 | 修改 CMD 的候选在构建前拒绝，未产生构建 attempts |
| build-failed | true | FAILED / 1 | 注入 `RUN exit 23`，第二轮构建失败且没有进入功能验证 |
| runtime-timeout | true | TIMED_OUT / 1 | 延迟 10 秒、运行预算 1 秒，正确超时并完成容器清理 |

超时场景保存了 `fault-injection.json`。清理检查对记录的容器 ID 执行 inspect，Docker 返回 `No such container`，证明超时容器已删除。

结构化证据哈希：

- `gate-result.json`：`7347bb0b1e117fde60edf2da6cff58888c637a41a61eab9556fefa26a6490652`
- `results.csv`：`67357ef26ae8bf8da04440bbad32505c110e10f1739c9fb8106741c246e426c3`

## 5. 状态、退出码和场景通过的区别

工作流状态描述工具实际到达的终态，例如 `SUCCEEDED`、`FAILED` 或 `TIMED_OUT`；工作流 CLI 退出码让调用方识别本次运行是否成功；`case.passed` 表示实际结果是否符合该故障场景预期。因此故意注入错误的场景可以是工作流退出 1、状态 FAILED，但场景本身 `passed=true`。

## 6. GitHub CI 范围核查

服务器已安装 GitHub CLI，但当前 `gh auth status` 显示未登录；本次最新 `main` 中也没有 `.github/workflows/` 文件。因此个人本地 Gate 可以完整完成，但组级 GitHub Actions、main 分支保护以及“故意失败被拦截—同一 PR 修复—成功合并”的证据当前不具备执行前提。

这些步骤按课程手册应由组长使用仓库管理员权限在全组仓库执行一次。本文不把未执行的 CI、分支保护或拒绝合并标为完成；验收表保持 PENDING，待组长提供共同 PR、运行链接与 artifact 后补录。

## 7. 证据索引

| 内容 | 服务器相对路径 |
|---|---|
| 服务构建、镜像检查与 28 项测试 | `work/e7-241250078-build/` |
| 个人边界测试定向结果 | `work/e7-241250078-targeted/` |
| Gate 包装命令与退出码 | `work/e7-241250078-gate/driver/` |
| Gate 汇总报告 | `work/e7-241250078-gate/gate/gate-result.json` |
| 六项结果表 | `work/e7-241250078-gate/gate/results.csv` |
| 各场景原始输入、命令和日志 | `work/e7-241250078-gate/gate/<case>/` |
| 超时故障说明 | `work/e7-241250078-gate/gate/runtime-timeout/fault-injection.json` |
| 超时容器清理核验 | `work/e7-241250078-gate/gate/runtime-timeout/evidence/cleanup-check/` |

`work/` 不进入 Git，将在服务器个人提交目录中单独归档。Git 提交仅包含本人 E7 测试、报告和验收记录。
