本样例用于 B08 E3 的 MDFixer 混合声明修复基线。

- 原作者与来源：A08，https://github.com/LoShell/DevOps-Course-Assignment-A08。
- 参考源码版本：`f8584a58e7be9d39ca630b5c6617a9ed25e8e4da`。
- 原目录：`E3/fixtures/md-rd/`。
- 原始故障样例提交：`8a9cfc46d854e697fd397c1f6c579014e219144b`，由 A08 文档记录。
- 复用范围：Makefile、src/main.c、include/common.h、include/config.h、include/unused.h。
- 上述源码保留原有 MD 与 RD，B08 在独立副本中验证只修复 MD 的参考补丁。
- B08 新增内容：固定 MD 修复输入、参考及失败候选补丁、验证与恢复脚本、B08 自己的运行证据和操作说明。
- 代码与材料由 Codex 辅助准备；个人身份、贡献认领和人工审阅须由实际成员确认。

目标规则为 `build/main.o: src/main.c $(HEADERS)`，同时包含直接项和变量项，因此按 E3 课件归类为 HYBRID。
MD 为遗漏 include/config.h；RD 为多声明 include/unused.h。参考补丁仅补 MD，保留 RD，便于单独验证修复效果。
