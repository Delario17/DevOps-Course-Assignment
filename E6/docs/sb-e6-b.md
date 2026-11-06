# E6-B 两轮构建与程序验证报告（241250078 孙博一）

## 1. 基本信息

- 小组/轨道：B08 / B（DRAFT）
- 姓名/学号：孙博一 / 241250078
- 实验日期：2026-11-06（Asia/Shanghai）
- 仓库：`https://github.com/Delario17/DevOps-Course-Assignment`
- 服务器目录：`/root/241250078/B08-remote-repo/E6`
- 同步的上游版本：`0fabae011f2ad8cf917b4c0a24eeb817ab46d24c`
- 本人测试实现提交：`dd1618f721b85a5d603d72ca97d68fd885f5dd23`
- 分支：`student/241250078/e5-e7`

## 2. 环境与基线

环境自检无 problems。服务器为 Ubuntu 22.04.5 LTS、x86_64、2 CPU、1.7 GiB 内存；Docker 29.1.3、Compose 2.40.3、Python 3.10.12。资源低于建议值的 warnings 原样保留在 `work/e6-241250078-doctor/env.json`。

修改前服务构建退出码为 0，完整单元测试为 `26 passed in 0.25s`，证据目录为 `work/e6-241250078-build-before/`。

## 3. 候选来源

本次明确使用 `--replay`，复用包内保存的 DeepSeek E5 候选，没有声称进行新的模型/API 调用。

- 候选：`fixtures/ci-candidates/DeepSeek-E5.Dockerfile`
- 来源记录：`fixtures/ci-candidates/provenance.json`
- 本次实际运行候选 SHA-256：`1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e`
- 选择原因：候选保留固定基础镜像与项目、构建和运行指令，仅增加 `build-essential` 以修复缺少 `make` 的根因。

仓库来源记录中的旧 `sha256` 字段为 `ede21b...`，与当前候选文件实际哈希不一致；本报告不沿用该旧值，使用 `invocation.json`、`result.json` 和实际文件共同记录的 `1f94ff...`。该差异已在个人候选来源记录中说明。

## 4. 两轮构建与验证

最终运行命令：

```bash
python3 scripts/course.py e6 --replay \
  --out work/e6-241250078-after --build-timeout 1200
python3 scripts/verify_e6_b_evidence.py \
  --run-dir work/e6-241250078-after/evidence
```

结果：

| 阶段 | 结果 |
|---|---|
| E6 入口 | 退出码 0，`SUCCEEDED` |
| 第一轮故障构建 | 退出码 1，`MISSING_MAKE` |
| 原始失败 | `/bin/sh: 1: make: not found` |
| 第二轮候选构建 | 退出码 0 |
| 第二轮镜像 ID | `sha256:aaf25d0bed23ed18febf12332ac7b775dfa5176e02c4a4d9024d4651ed2fb539` |
| 同镜像 ID 运行 | 退出码 0，`--network none` |
| 标准输出 | `hello E3` |
| 输出比较 | `output_matches=true` |
| 证据校验 | `passed=true`，退出码 0 |

第一轮必须真实到达 `RUN make` 并被分类为 `MISSING_MAKE`，网络故障或其他编译错误不能算成功复现。第二轮构建成功后通过 `docker image inspect` 取得镜像 ID；验证命令最后一个参数使用该同一 ID，而不是可变标签，并同时检查退出码与输出文本。

## 5. 本人新增测试

新增 `services/draft/tests/test_student_241250078_e6.py`，验证候选即使保留全部指令，但调换 `WORKDIR` 与 `COPY` 的顺序，也会被 `prepare_candidate` 在构建前拒绝，并返回 `Candidate changed required project/build/runtime instructions`。

这项测试保证候选不能通过“指令都存在”绕过原始构建语义的顺序约束。修改后重新构建服务镜像，完整结果为 `27 passed in 0.18s`，退出码 0，证据位于 `work/e6-241250078-build-after/`。随后重新执行 E6，原始两轮流程仍通过。

## 6. 核心机制理解

1. `instructions` 去除空行和注释，并合并反斜杠续行。
2. `prepare_candidate` 检查摘要固定的单阶段 `FROM`，并要求原始项目、构建、运行指令按顺序保留；只允许额外增加修复用 `RUN`。
3. `classify_failure` 将缺少 make、基础设施故障和其他构建错误分开。
4. `auto_build` 先运行故障基线，确认 `MISSING_MAKE` 后才构建候选；第二轮成功后保存镜像 ID，再用同一 ID 进行禁网验证。
5. 验证只有在退出码为 0 且输出精确匹配 `hello E3` 时才成功。

## 7. 证据索引

| 内容 | 服务器相对路径 |
|---|---|
| 环境自检 | `work/e6-241250078-doctor/env.json` |
| 修改前构建与 26 项测试 | `work/e6-241250078-build-before/` |
| 修改前两轮运行 | `work/e6-241250078-before/` |
| 修改后构建与 27 项测试 | `work/e6-241250078-build-after/` |
| 最终两轮运行与程序验证 | `work/e6-241250078-after/` |
| 最终结构化结果 | `work/e6-241250078-after/evidence/result.json` |
| 两轮 Dockerfile 与构建日志 | `work/e6-241250078-after/evidence/iter-01/`、`iter-02/` |
| 程序输出 | `work/e6-241250078-after/evidence/verify.log` |

`work/` 按仓库规则不进入 Git，将在服务器个人提交目录中另行归档；Git 提交包含本人测试、报告、验收记录和候选来源记录。

## 8. 当前范围

本报告只声明完成 E6-B；E7 五场景、远程 CI 和分支保护尚未执行，不将其标记为完成。

正式执行 `scripts/secret_scan.py . --history --image course1027-draft:241250078` 时退出码为 1，匹配来自共享仓库早期提交 `63252533ed1fc3aba98109cb9a89c634af4bf777` 的 Git 历史；当前 `HEAD` 的 E6 树没有对应匹配，本人新增测试和三份文档的定向扫描也为干净。该共享历史问题不在本次个人 E6 修改范围内，因此没有改写历史；原始扫描输出保存在 `work/e6-241250078-meta/secret-scan.txt`。
