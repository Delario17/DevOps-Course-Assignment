# MDFixer HYBRID 复现与审阅记录

- 状态：`APPROVED_WITH_AI_ASSISTED_REVIEW`。
- 复现人及确认人：盛浩宇，241250008，GitHub `lejuwujiang258`。
- 确认日期：2026-10-09（北京时间）。
- 本人复现时间：2026-10-09 13:37:14.630641 至 13:37:39.512063。
- 证据目录：[`evidence/20261009T133714630641+0800/`](evidence/20261009T133714630641+0800/)。
- 运行结果：40/40 PASS，39 条命令及原始日志完整。
- 审阅方式：Codex 完成技术核对，盛浩宇阅读并确认结论与本人运行结果一致。

## 技术核对

- [x] `main.c` 读取 `config.h`，原 Makefile 的 `HEADERS` 未声明 `config.h`；GCC 依赖输出与 Make 数据库一致。
- [x] 修复前 `CONFIG_VALUE` 4→5 的普通构建输出 10，相同源码完整重建输出 11。
- [x] 参考补丁只补充 `config.h`，保留原有 `unused.h` RD，与案例限定的 MD 修复范围一致。
- [x] 修复后两次头文件单独变更均触发重编译，输出依次为 11 和 12。
- [x] 失败候选退出码为 2，拒绝后恢复有效 Makefile；恢复字节一致，重新构建输出 12。
- [x] 固定源码提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` 与实际 fixture 一致；运行时提交为 `d293999a0c7af3674768f311ad53fc171e01c0aa`。
- [x] 环境、源码、脚本、Oracle 和补丁哈希一致，阶段输出与 `observations.json` 相符。
- [x] `commands.txt` 与 JSON 中 39 条命令的标准输出、错误输出和退出码一致。

## 结论

HYBRID 参考补丁修复了 `include/config.h` 的缺失依赖，两次增量验证均触发正确重建；失败候选被拒绝并成功恢复，证据链完整。
