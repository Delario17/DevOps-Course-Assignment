# E5 B 组：失败反馈、模型候选与手工复建

位置：服务器上自己的 B 仓库。前置：完成 E5—E7 代码升级与构建，基线服务单测24项通过。模型交互在电脑浏览器进行，候选文件回到服务器保存。

## 1. 查看构建任务

```bash
cat fixtures/draft/README.md
cat fixtures/draft/main.c
cat fixtures/draft/Makefile
cat fixtures/draft/Dockerfile.broken
head -n 1 fixtures/ci-candidates/DeepSeek-E5.Dockerfile
```

输入：Tiny Greeting 源码、Makefile、README、初始 Dockerfile。程序功能验证命令为 `./hello`，标准输出应为 `hello E3`、退出0。初始 Dockerfile 使用未装 make 的 Python 基础镜像。

E5 入口会把初始 Dockerfile 的 FROM 统一为候选里的固定 digest，并保存当次实际使用的文件。下文始终以 `work/e5-01/iter-01/Dockerfile` 为本次初始输入。

## 2. 执行并保存初始失败

```bash
python3 scripts/course.py e5 --out work/e5-01 --build-timeout 1200
E5_CODE=$?
printf 'E5_EVIDENCE_EXIT_CODE=%s\n' "$E5_CODE"
git rev-parse HEAD > work/e5-01/source-commit.txt
cat work/e5-01/iter-01/Dockerfile
cat work/e5-01/iter-01/result-retry.json
grep -n 'make: not found' work/e5-01/iter-01/build-retry.log
```

输入：初始 Dockerfile 和项目。输出：镜像构建到达 `RUN make`，日志包含 `/bin/sh: 1: make: not found`。镜像内部这条命令通常退出127，外层 docker build 退出1。采集脚本把目标失败和提示保存成功，因此 `E5_EVIDENCE_EXIT_CODE=0`。

|结果路径|内容|
|---|---|
|project/|本次项目副本|
|iter-01/Dockerfile|实际初始构建输入|
|iter-01/build/stdout.log、stderr.log|完整构建输出|
|iter-01/build/exit-code.json|Docker命令退出码|
|iter-01/build-retry.log|合并后的初始失败日志|
|iter-01/result-retry.json|build_exit_code|
|iter-01/prompt-error-driven.txt|Dockerfile与错误日志提示|
|iter-01/prompt-context-driven.txt|进一步提供README的提示|

网络错误或下载超时会使采集入口失败。此时查看 build 日志，恢复构建条件后在 `work/e5-02` 重跑。

## 3. 取得两个模型候选

```bash
cat work/e5-01/iter-01/prompt-error-driven.txt
cat work/e5-01/iter-01/prompt-context-driven.txt
```

操作者：每组负责候选实验的学生。输入：两种提示全文。电脑端新建两次对话，分别提交提示；保存模型名称、时间、提示和原始回复。每类提示请求3个候选，分别编号，例如错误驱动error-01/02/03，上下文驱动context-01/02/03。比较是否补全make/C编译工具、是否保留FROM、COPY、RUN make和CMD，再说明选择理由。

选择时按原课件的R1—R4顺序记录：R1排除本轮此前已构建过的候选；R2优先多候选一致的方案，文本续行归一化的具体规则写入记录；R3检查候选是否包含与失败相关的核心依赖关键词；R4仍无法区分时，把候选交给模型选择并保存该次回复。单次课堂至少保存最终候选及其选择过程，完整候选对照保留在本组实验记录。

服务器保存：

```bash
mkdir -p work/candidate-01 work/candidate-02 work/candidate-03
nano work/candidate-01/Dockerfile
```

粘贴第一个候选的Dockerfile正文，Ctrl+O、Enter保存，Ctrl+X退出。用同样方法编辑 `work/candidate-01/model-response.txt`，保存完整原始回复；其余候选依次保存，来源表写清对应哪类提示。也可以通过SFTP上传文件。

候选应保留与本次初始输入相同的 FROM digest，以及这些项目操作：

```dockerfile
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

新增依赖安装通常为 `apt-get update` 后安装 `build-essential`。按模型真实回复记录修改，保留原始版本和人工调整说明。

```bash
cp -n course-support/templates/候选来源记录.json work/candidate-01/来源记录.json
nano work/candidate-01/来源记录.json
diff -u work/candidate-01/Dockerfile work/candidate-02/Dockerfile
```

输入：候选与来源模板。输出：填好的来源和候选差异。`diff` 返回1表示文件有差异。

## 4. 选定候选

采用自己的候选时：

```bash
CANDIDATE_FILE=work/candidate-01/Dockerfile
test -f "$CANDIDATE_FILE"
sed -n '1,180p' "$CANDIDATE_FILE"
```

课堂预演也可选随包 DeepSeek 记录候选：

```bash
CANDIDATE_FILE=fixtures/ci-candidates/DeepSeek-E5.Dockerfile
sed -n '1,180p' "$CANDIDATE_FILE"
```

两条路线选一条，把选择写到报告。自生成路线保存提示、原始回复和选择依据；记录候选路线标记“包内已保存 DeepSeek 候选”。

## 5. 手工构建选定候选

```bash
SID=$(git config --local user.name)
CANDIDATE_IMAGE="course1027-e5-candidate:$SID"
docker build --progress=plain -f "$CANDIDATE_FILE" \
  -t "$CANDIDATE_IMAGE" work/e5-01/project \
  > work/e5-01/candidate-build.log 2>&1
CANDIDATE_CODE=$?
printf 'CANDIDATE_BUILD_EXIT_CODE=%s\n' "$CANDIDATE_CODE"
tail -n 40 work/e5-01/candidate-build.log
```

输入：选定 Dockerfile，构建上下文为本次项目副本。输出：完整候选构建日志，预期退出0。命令运行时日志写文件，可在另一 SSH 窗口执行 `tail -f 完整日志路径` 查看，Ctrl+C 结束日志查看。

构建退出0后再执行下一步。失败时根据日志继续修订候选并保留新版本，重新编号日志。

## 6. 按本次镜像 ID 验证功能

```bash
IMAGE_ID=$(docker image inspect "$CANDIDATE_IMAGE" --format '{{.Id}}')
printf '%s\n' "$IMAGE_ID" > work/e5-01/candidate-image-id.txt
docker run --rm --network none --cpus 1 --memory 256m --pids-limit 64 "$IMAGE_ID" \
  > work/e5-01/verify.log 2> work/e5-01/verify-stderr.log
VERIFY_CODE=$?
printf 'VERIFY_EXIT_CODE=%s\n' "$VERIFY_CODE"
printf '%s\n' "$VERIFY_CODE" > work/e5-01/verify-exit-code.txt
cat work/e5-01/verify.log
```

输入：刚构建的同一镜像 ID。预期程序退出0、输出 `hello E3`。镜像构建成功和程序行为正确是两项独立记录。

## 7. 写复现说明

在 `docs/e5-b.md` 保存：源码 SHA、初始 Dockerfile、缺 make 关键行、两种提示、原始回复、候选比较及选择、人工修改、候选构建退出码、镜像 ID、功能验证结果。把服务器路径对应到实际文件。

论文方法通过失败日志与上下文生成/选择 Dockerfile；本次课堂流程通过网页取得并保存候选，在服务容器与宿主 Docker 环境中复建。记录模型、交互方式、项目规模和运行环境的具体设置。

E6 将这套已取得候选的构建与验证过程写入自动工作流，操作见 [E6 B](../04_E6核心实现/B组操作手册.md)。
