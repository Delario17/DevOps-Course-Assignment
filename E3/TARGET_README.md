# 盛浩宇：Target 直接声明案例

## 故障、修复和失败候选

`src/main.c` 实际使用 common.h 和 config.h，程序输出 COMMON_VALUE + CONFIG_VALUE。初始值为 6+4=10。
故障 Makefile 为 `build/main.o: src/main.c include/common.h`，漏掉 config.h。因此只把 CONFIG_VALUE 改为 5 时，make 不重新编译，程序仍为 10；完整重建才是 11。
参考补丁直接把规则改成 `build/main.o: src/main.c include/common.h include/config.h`。修复后不先 clean，连续两次只改配置值得到 11、12，并且编译日志、产物时间戳和哈希都验证了重新编译。
无效补丁基于参考补丁后的 Makefile，在编译前插入 `false`；用 make -B -j2 强制执行，退出码 2，候选被拒绝。脚本恢复上一个有效 Makefile 的原始字节，完整构建及功能验证输出 12。

## 固定输入与来源

- Fixture：`fixtures/mdfixer-target/`；固定提交 `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a`。
- Oracle：`oracle/mdfixer-target.expected.json`；只包含 config.h 的 MISSING finding。
- 声明：课件 Target，对应接口枚举 DEPENDENCY_LIST；没有 HEADERS/DEPS 依赖变量或 .d 文件，没有项目内 RD。
- C 源码来自 B08 已合并 Hybrid，原始 A08 归属与参考版本见 `fixtures/mdfixer-target/SOURCE.md`。
- 原始故障 Fixture 永久保留；两个补丁均作用于临时副本根目录的 Makefile。

## 实际验证

- 执行时间：2026-10-11 11:09:59 至 11:10:07，北京时间。
- 执行者：Codex automated Linux execution for Sheng Haoyu; Target human review pending。
- 环境：Ubuntu 24.04 WSL、x86_64、GCC 13.3.0、GNU Make 4.3、Python 3.12.3。
- 配置：`b08-target-74f06528d5480265`。
- 技术结果：44/44 PASS，39 条原始命令；唯一非零退出为预期无效候选，退出码 2。
- [运行 README](evidence/mdfixer-target/20261011T110959885929+0800/README.md)、[observations.json](evidence/mdfixer-target/20261011T110959885929+0800/observations.json)、[commands.txt](evidence/mdfixer-target/20261011T110959885929+0800/commands.txt)。
- Codex 另行核对了所有输入/脚本哈希、固定提交文件、捕获补丁、命令与 JSON、实际输出、恢复字节以及两份决定 JSON，均相符。
- 人工确认：见 [HUMAN_REVIEW.md](HUMAN_REVIEW.md) 和 [review.json](oracle/mdfixer-target.review.json)，当前待成员阅读确认；不沿用 Hybrid 确认。

## 本人负责项验收

- [x] 故障项目及来源、版本固定。
- [x] MD-only Oracle 与预期结果。
- [x] 直接声明参考 Patch。
- [x] 基于有效版本的无效 Patch。
- [x] 修复前增量错误与 clean 对照。
- [x] 修复后两次头文件变更均自动重编译。
- [x] Make 展开依赖与 GCC -MM 项目依赖相等，原问题已补齐。
- [x] 无效候选拒绝、精确恢复、恢复后构建和功能成功。
- [x] 原始命令、环境、哈希、JSON 和 README。
- [x] Hybrid 当前状态整理，原证据保留。
- [ ] Target 成员辅助审阅确认。

执行方式见 [MANUAL_STEPS.md](MANUAL_STEPS.md)。本文件及 run_mdfixer_target.py 可供 Macro 负责人接入统一执行入口。
