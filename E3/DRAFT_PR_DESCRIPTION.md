# E3 DRAFT Tiny Greeting 测试基线

新增一个固定版本的 C/Make 项目，用于验证 DRAFT 生成的构建环境。项目通过 `make` 构建，运行 `./hello` 应输出 `hello E3`。

失败候选 `Dockerfile.broken` 在 Debian slim 中直接执行 `make`，预期因缺少工具链失败。参考环境 `Dockerfile.reference` 安装 `gcc`、`make` 和 `libc6-dev` 后完成同一项目构建与功能验证。验证脚本把两份 Dockerfile 绑定到同一基础镜像 RepoDigest，并记录基础镜像、参考镜像、命令、退出码和输出。

固定输入提交为 `5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43`。王祎于 2026-10-12 发起完整复现，24/24 项断言通过，19 条命令完整记录。失败镜像构建退出码为 1 并命中 `make: not found`；参考镜像构建成功，容器输出 `hello E3`，退出码为 0。最终证据位于 `E3/evidence/draft-tiny-greeting/20261012T105358976530+0800/`，证据提交为 `acdea5f45ed6ab73c600b8ffb438f8e9605c2847`。
