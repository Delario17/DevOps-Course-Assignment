# Macro 样例来源

朱雨乐（241250011）的 B08 E3 任务；按课件第 35 页的 Macro 风格准备。

- C 源码、common.h、config.h 复用本仓库 HYBRID 样例，固定参考提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`。
- 上游归属：A08，https://github.com/LoShell/DevOps-Course-Assignment-A08；参考提交 `f8584a58e7be9d39ca630b5c6617a9ed25e8e4da`，目录 `E3/fixtures/md-rd/`。
- 新增 Makefile 使用 `build/main.o: $(DEPS)`，源文件和头文件都由 DEPS 提供。移除原 HYBRID 的 unused.h RD，仅留下 config.h MD。
- COMMON_VALUE=6、CONFIG_VALUE=4，初始输出 10；仅改 CONFIG_VALUE 为 5，故障增量仍输出 10，clean 输出 11。
- 参考补丁只在 DEPS 加入 include/config.h，不修改目标规则或 recipe。
- Codex 辅助准备和自动执行；未声称本人手写或已完成个人审阅。
