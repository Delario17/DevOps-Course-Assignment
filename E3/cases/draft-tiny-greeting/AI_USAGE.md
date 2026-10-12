# DRAFT Tiny Greeting AI 使用记录

- 工具：Codex。
- 日期：2026-10-11 至 2026-10-12，Asia/Shanghai。
- 任务：在独立分支完成 B08 的 DRAFT 基线，并核对成员发起的 Docker 复现证据。
- AI 编写：最小 C/Make 项目、失败与参考 Dockerfile、人工 Oracle、验证脚本、基线说明和 PR 说明。
- 核心设计：失败环境与参考环境使用同一 Debian 基础镜像 RepoDigest，将可观察差异集中在构建工具链，并同时验证构建与程序行为。
- 固定输入提交：`5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43`。
- AI 首次执行：在 macOS arm64 上运行本机构建、程序行为、版本输出、功能测试及 Dockerfile 静态约束，18/18 PASS。
- 首次证据：[`evidence/20261011T141102041611+0800/`](evidence/20261011T141102041611+0800/)，状态 `PARTIAL`。
- 本人复现：王祎于 2026-10-12 使用 Python 3.12.14 和 Docker Desktop 4.94.0 发起 `--docker required` 完整验证。
- 最终结果：24/24 PASS，记录 19 条命令；失败镜像退出码 1，参考容器输出 `hello E3`。
- 最终证据：[`evidence/20261012T105358976530+0800/`](evidence/20261012T105358976530+0800/)。
- 最终证据提交：`acdea5f45ed6ab73c600b8ffb438f8e9605c2847`。
- 辅助审阅：Codex 核对 JSON、命令日志、镜像 digest、镜像 ID、失败签名和文件哈希，结论写入 [`REVIEW.md`](REVIEW.md)。
