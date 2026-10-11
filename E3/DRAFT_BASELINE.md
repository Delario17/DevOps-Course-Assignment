# B08 E3：DRAFT Tiny Greeting 基线

## 目标

本基线用一个最小 C 项目检验 DRAFT 生成环境的能力。项目逻辑固定，环境生成结果需要同时满足“能够完成构建”和“程序行为正确”。失败样例与参考样例使用同一基础镜像 digest，使差异集中在工具链是否存在。

## 固定输入

| 项目 | 内容 |
|---|---|
| 项目 | Tiny Greeting |
| 固定提交 | `5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43` |
| 工作目录 | `E3/fixtures/draft-tiny-greeting/` |
| 构建命令 | `make` |
| 功能验证 | `./hello`，预期输出 `hello E3` |
| 版本验证 | `./hello --version`，预期输出 `tiny-greeting 1.0.0` |
| 基础镜像标签 | `debian:bookworm-slim` |

验证脚本在 Docker 运行时先执行 `docker pull` 并取得 RepoDigest，然后把同一 digest 传给两份 Dockerfile。证据记录基础镜像 ID、RepoDigest、参考镜像 ID、构建日志、退出码和容器输出。

## 两个环境候选

`Dockerfile.broken` 直接运行 `make`，没有安装构建工具。预期镜像构建非零退出，日志出现 `make: not found`。

`Dockerfile.reference` 安装 `gcc`、`make` 和 `libc6-dev`，随后执行相同的 `make`。预期镜像构建成功，容器运行输出 `hello E3`，退出码为 `0`。

## 自动验证

在仓库根目录运行：

```bash
python3 E3/scripts/run_draft_baseline.py \
  --operator "姓名（本人发起复现）" \
  --docker required
```

脚本每次创建新的 `E3/evidence/draft-tiny-greeting/<时间>/`，不会覆盖历史证据。输出包括：

- `commands.txt`：每条命令的标准输出、错误输出和退出码；
- `observations.json`：环境、Commit、配置标识、哈希和全部断言；
- `native-validation.json`：本机构建与功能验证；
- `docker-validation.json`：失败镜像和参考镜像的判断结果；
- `input/`：本次运行使用的源码、Makefile、Dockerfile 和 Oracle 快照。

## 当前验证状态

2026-10-11 的 macOS 本机验证记录位于 `evidence/draft-tiny-greeting/20261011T141102041611+0800/`：

- 固定输入校验通过；
- 本机构建、程序输出、版本输出和 `make test` 通过；
- Dockerfile 静态约束通过；
- 共 18/18 项断言通过；
- 当前机器没有 Docker，容器验证状态为 `UNAVAILABLE`，总体记录为 `PARTIAL`。

Docker 环境复现并生成 `PASS` 记录后，DRAFT 基线达到最终验收状态。
