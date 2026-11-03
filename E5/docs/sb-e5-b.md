# E5-B 论文复现个人报告（241250078 孙博一）

## 1. 实验身份与环境

- 小组：B08
- 分工：B 轨（DRAFT / Dockerfile 修复）
- 学号：241250078
- 姓名：孙博一
- 实验日期：2026-11-01（Asia/Shanghai）
- 服务器工作目录：`/root/241250078/B08-remote-repo/E5`
- 源代码提交：`a1d731a2418c7f545e2c0600083d3220b9f2d3bb`
- 本次证据目录：`work/e5-241250078-01/`

## 2. 前置检查

最新 `main` 已拉取到个人目录。在 `make all` 的 pytest 阶段得到 `24 passed in 0.41s`，日志位于 `work/20261101-030533/test.log`。pytest 完成后 Compose 客户端未自动退出，因此没有把该次 `make all` 记作完整成功；后续 E5 正式实验命令和 Docker 验收均独立完成。

## 3. 初始失败复现

执行：

```bash
python3 scripts/course.py e5 --out work/e5-241250078-01 --build-timeout 1200
```

初始构建退出码为 `1`。关键失败行为：

```text
/bin/sh: 1: make: not found
```

对应证据：

- `work/e5-241250078-01/iter-01/build/exit-code.json`
- `work/e5-241250078-01/iter-01/build/build.log`
- `work/e5-241250078-01/iter-01/error-localization.json`

## 4. 两类提示词与候选选择

实验脚本生成并保存了两类提示词：

- 错误驱动：`work/e5-241250078-01/iter-01/prompt-error-driven.txt`
- 上下文驱动：`work/e5-241250078-01/iter-01/prompt-context-driven.txt`

本次采用实验包提供并留有来源记录的 DeepSeek 候选，而不是宣称进行了新的在线模型调用：

- 候选来源：`fixtures/ci-candidates/DeepSeek-E5.Dockerfile`
- 来源元数据：`fixtures/ci-candidates/provenance.json`
- 实验副本：`work/e5-241250078-01/candidate-recorded-deepseek/Dockerfile`
- 选择说明：`work/e5-241250078-01/selection.txt`
- 候选 Dockerfile SHA-256：`1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e`

该候选保留原有 `FROM`、`WORKDIR`、`COPY`、`RUN make` 和 `CMD`，在编译前安装 `build-essential`，直接修复 `make` 缺失的根因。

## 5. 修复构建与严格验收

候选镜像：`course1027-e5-candidate:241250078`

- 修复构建退出码：`0`
- 实际镜像 ID：`sha256:b6300f7ddcdff4263c943cdacea493d0a3616b383943bde89742e061d0fb1860`
- 构建日志：`work/e5-241250078-01/candidate-build.log`
- 镜像 ID 记录：`work/e5-241250078-01/candidate-image-id.txt`

使用上述同一镜像 ID，在断网和资源限制条件下运行：

```bash
docker run --rm --network none --cpus 1 --memory 256m --pids-limit 64 \
  sha256:b6300f7ddcdff4263c943cdacea493d0a3616b383943bde89742e061d0fb1860
```

验收结果：

- 退出码：`0`
- 标准输出：`hello E3`
- 标准错误：空
- 证据：`work/e5-241250078-01/verify.log`、`verify-stderr.log`、`verify-exit-code.txt`

## 6. 结论

初始失败已可重复复现，根因定位为基础镜像缺少 `make`/编译工具链；采用带来源记录的 DeepSeek 候选安装 `build-essential` 后，镜像构建成功，并通过同一镜像 ID 的受限运行验收，最终输出 `hello E3`。
