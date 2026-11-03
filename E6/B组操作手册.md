# E6 B 组：两轮构建与程序验证

位置：自己的 B 仓库。前置：E5已保存候选、来源与初始失败。输入为 `fixtures/draft/`、候选 Dockerfile、程序预期 `hello E3`。

## 1. 选择本次候选来源

自己的候选路线：

```bash
python3 scripts/course.py e6 \
  --candidate work/candidate-01/Dockerfile \
  --out work/e6-own --build-timeout 1200
E6_CODE=$?
printf 'E6_EXIT_CODE=%s\n' "$E6_CODE"
B6=work/e6-own/evidence
```

包内记录候选路线：

```bash
python3 scripts/course.py e6 --replay \
  --out work/e6-replay --build-timeout 1200
E6_CODE=$?
printf 'E6_REPLAY_EXIT_CODE=%s\n' "$E6_CODE"
B6=work/e6-replay/evidence
```

选其中一段执行。输出：整体成功退出0。`invocation.json` 记录来源和候选内容哈希；`evidence/result.json` 给出两轮执行结果。

## 2. 逐轮查看

```bash
python3 -m json.tool "$B6/result.json"
cat "$B6/iter-01/Dockerfile"
cat "$B6/iter-02/Dockerfile"
cat "$B6/verify.log"
```

|步骤|输入|处理|输出|
|---|---|---|---|
|候选校验|初始与候选Dockerfile|检查固定FROM和项目/构建/运行指令|有效候选继续，无效候选退出|
|第一轮|缺make的初始Dockerfile|真实docker build|build_exit_code=1，failure_class=MISSING_MAKE|
|第二轮|保存的有效候选|安装依赖、真实构建|build_exit_code=0，保存image_id|
|镜像检查|第二轮镜像|docker image inspect|iter-02/image-inspect.json|
|程序验证|第二轮同一image_id|禁网启动，记录stdout/exit|exit_code=0，hello E3，output_matches=true|
|报告|输入、两轮日志和验证|汇总编号、来源、状态|result.json，SUCCEEDED|

B 服务执行构建时使用 bridge 网络，以便 Docker 客户端完成注册表认证和下载；最终被测程序使用 `--network none`。

## 3. 结果目录

```text
work/e6-own/ 或 work/e6-replay/
  invocation.json
  runner/command.json stdout.log stderr.log exit-code.json
  evidence/
    project/                  实际项目副本
    iter-01/Dockerfile         初始输入
    iter-01/build-stdout.log build-stderr.log
    iter-02/Dockerfile         实际候选
    iter-02/build-stdout.log build-stderr.log
    iter-02/image-inspect.json
    verify.log verify-stderr.log
    verify-container-id.txt
    result.json
```

输入副本中保留本次实际文件，候选和验证镜像可通过报告逐项关联。

## 4. 校验保存的证据

```bash
python3 scripts/verify_e6_b_evidence.py --run-dir "$B6"
```

输入：本次 evidence。输出：`passed=true`、MISSING_MAKE、固定构建退出0、验证退出0、hello E3、镜像 ID 与候选哈希。校验脚本检查报告与文件对应关系。

## 5. 核心代码阅读

```bash
sed -n '1,170p' services/draft/draft/autobuild.py
```

|函数|输入|输出|
|---|---|---|
|instructions|Dockerfile文本|合并续行后的逻辑指令|
|prepare_candidate|初始Dockerfile、候选|验证必需指令并固定初始FROM|
|classify_failure|构建日志|MISSING_MAKE、INFRASTRUCTURE或OTHER_BUILD_ERROR|
|execute|命令、日志路径、超时|进程退出码和完整输出|
|auto_build|项目、候选、输出、期望、预算|两轮构建、运行验证和结构化报告|

学生根据实际记录解释为什么第一轮必须到达缺 make，第二轮如何产生最终镜像，以及运行检查怎样使用同一 image_id。扩展一项失败测试或候选处理逻辑后重新构建对应服务镜像。

## 6. 失败的分支

候选校验失败时查CLI输出中的 `error`。初始轮若为网络故障，先修复基础设施；候选构建失败时查看 iter-02 日志；运行返回非0或输出不匹配时查 verify.log 与 verify-stderr.log。每次修订保留新目录，记录本次候选及具体失败原因。

E7 使用这些分支建立完整验证矩阵，随后连接远程 CI。
