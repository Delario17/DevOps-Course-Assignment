# MDFixer HYBRID 复现与审阅记录

- 状态：`APPROVED_WITH_AI_ASSISTED_REVIEW`。
- 复现人及确认人：盛浩宇，241250008，GitHub `lejuwujiang258`。
- 确认日期：2026-10-09（北京时间）。
- 本人复现时间：2026-10-09 13:37:14.630641 至 13:37:39.512063。
- 证据目录：[`evidence/20261009T133714630641+0800/`](evidence/20261009T133714630641+0800/)。
- 运行结果：40/40 PASS，39 条命令。
- 结构化索引：[`oracle/review.json`](oracle/review.json)。

## 技术核对

- [x] `main.c` 读取 `config.h`，原 Makefile 的 `HEADERS` 未声明 `config.h`。
- [x] 修复前 4→5 的增量构建输出 10，相同源码完整重建输出 11。
- [x] 参考补丁补充 `config.h`，保留原有 `unused.h` RD。
- [x] 修复后两次头文件单独变更均触发重编译，输出依次为 11 和 12。
- [x] 失败候选退出码为 2，拒绝后恢复有效 Makefile，重建输出 12。
- [x] 固定源码、命令日志、JSON、Oracle 和补丁哈希相符。

## 结论

HYBRID 参考补丁修复了 `include/config.h` 的缺失依赖，同时保留案例中的 `unused.h` RD。盛浩宇本人发起复现，并确认辅助核查结论与运行结果一致。
