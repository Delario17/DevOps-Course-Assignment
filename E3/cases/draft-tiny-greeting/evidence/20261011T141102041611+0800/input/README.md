# Tiny Greeting DRAFT 输入项目

这是 B08 E3 的 DRAFT 环境生成基线。项目只有一个 C 源文件，便于把环境问题与项目自身复杂度分开。

## 构建与验证

```bash
make clean
make
./hello
./hello --version
make test
```

成功判据：

- `make` 退出码为 `0`，并生成可执行文件 `hello`；
- `./hello` 退出码为 `0`，标准输出严格等于 `hello E3`；
- `./hello --version` 标准输出严格等于 `tiny-greeting 1.0.0`；
- `make test` 退出码为 `0`。

## 容器样例

- `Dockerfile.broken`：基于 Debian slim，直接执行 `make`，由于没有安装构建工具而失败。
- `Dockerfile.reference`：在同一基础镜像中安装 `gcc`、`make` 和 `libc6-dev`，完成构建并以 `./hello` 作为容器入口。

两份 Dockerfile 都接受 `BASE_IMAGE` 构建参数。验证脚本先解析基础镜像 digest，再让失败样例和参考样例使用同一 digest。
