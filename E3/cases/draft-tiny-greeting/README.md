# B08 E3：DRAFT Tiny Greeting 基线

## 核心设计

本案例用一个逻辑固定的最小 C 项目测量 DRAFT 生成环境是否真正可用。失败环境与参考环境绑定同一 Debian 基础镜像 RepoDigest，唯一关键差异是构建工具链；验收同时检查编译成功、程序输出和版本输出。

## 案例产物

| 内容 | 位置 |
|---|---|
| 固定项目与两份 Dockerfile | [`fixture/`](fixture/) |
| 期望行为和固定版本 | [`oracle/expected.json`](oracle/expected.json) |
| 结构化审阅记录 | [`oracle/review.json`](oracle/review.json) |
| 自动验证脚本 | [`scripts/run.py`](scripts/run.py) |
| 历史运行证据 | [`evidence/`](evidence/) |
| 贡献和 AI 使用 | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md)、[`AI_USAGE.md`](AI_USAGE.md) |
| 复现审阅 | [`REVIEW.md`](REVIEW.md) |
| PR 说明 | [`PR_DESCRIPTION.md`](PR_DESCRIPTION.md) |

## 固定输入

| 项目 | 内容 |
|---|---|
| 项目 | Tiny Greeting |
| 固定提交 | `5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43` |
| 当前工作目录 | `E3/cases/draft-tiny-greeting/fixture/` |
| 固定提交中的原路径 | `E3/fixtures/draft-tiny-greeting/` |
| 构建命令 | `make` |
| 功能验证 | `./hello`，期望输出 `hello E3` |
| 版本验证 | `./hello --version`，期望输出 `tiny-greeting 1.0.0` |
| 基础镜像标签 | `debian:bookworm-slim` |

`Dockerfile.broken` 直接运行 `make`，因缺少工具链以非零状态退出并出现 `make: not found`。`Dockerfile.reference` 安装 `gcc`、`make` 和 `libc6-dev`，随后完成同一项目的构建和功能验证。

## 复现方法

在仓库根目录运行：

```bash
python3 E3/cases/draft-tiny-greeting/scripts/run.py \
  --operator "姓名（本人发起复现）" \
  --docker required
```

脚本在 `evidence/<时间>/` 创建新证据目录，记录命令标准输出、错误输出、退出码、环境信息、镜像身份和输入快照。

## 最终结果

王祎于 2026-10-12 在 macOS arm64 和 Docker Desktop 环境发起完整复现，证据位于 [`evidence/20261012T105358976530+0800/`](evidence/20261012T105358976530+0800/)：

| 检查项 | 实际结果 |
|---|---|
| 固定输入与 Commit | 通过 |
| 本机构建与功能验证 | 通过 |
| 失败镜像构建 | 退出码 `1`，命中 `make: not found` |
| 参考镜像构建 | 通过 |
| 参考容器行为 | 输出 `hello E3`，退出码 `0` |
| 容器内版本 | `tiny-greeting 1.0.0` |
| 总断言 | 24/24 PASS |

基础镜像固定为 `debian@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587`，参考镜像 ID 为 `sha256:0fac7d5dce6a00962f67ef9bc2505a15ea785d54576e21fb09991aa46007a1d0`。2026-10-11 的 PARTIAL 证据保留 Docker 安装前的本机基线。
