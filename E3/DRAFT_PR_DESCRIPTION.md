# E3 DRAFT Tiny Greeting 测试基线

新增一个固定版本的 C/Make 项目，用于验证 DRAFT 生成的构建环境。项目通过 `make` 构建，运行 `./hello` 应输出 `hello E3`。

失败候选 `Dockerfile.broken` 在 Debian slim 中直接执行 `make`，预期因缺少工具链失败。参考环境 `Dockerfile.reference` 安装 `gcc`、`make` 和 `libc6-dev` 后完成同一项目构建与功能验证。验证脚本把两份 Dockerfile 绑定到同一基础镜像 RepoDigest，并记录基础镜像、参考镜像、命令、退出码和输出。

固定输入提交为 `5d7ad3e534a67ca24e0adbb7271cb8b4540aeb43`。macOS 本机验证完成 18/18 项断言，构建、程序输出、版本输出和功能测试均通过。当前机器没有 Docker，因此现有证据状态为 `PARTIAL`；在 Docker 环境执行 `python3 E3/scripts/run_draft_baseline.py --operator "姓名" --docker required` 并取得 `PASS` 后完成最终验收。
