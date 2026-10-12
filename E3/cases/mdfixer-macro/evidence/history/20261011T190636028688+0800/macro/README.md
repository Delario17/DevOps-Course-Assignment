# MDFixer MACRO 实际运行记录

- 执行时间：2026-10-11T19:06:36.360052+08:00。
- 实际执行者：Codex automated Linux execution for Zhu Yule (241250011); human review pending。
- 固定样例提交：`4d72b7833d0adc561751486a2b656c82766a9484`。
- 运行时仓库提交：`8c4c9976f877144187943f1f2f371bcd47127631`。
- 配置标识：`b08-macro-85c0951fe9a1432f`。
- 结果：**PASS**，46/46 项断言通过。
- 人工审阅：待实际 B08 成员确认。

| 实验阶段 | 实际输出 |
|---|---|
| initial | 10 |
| before_fix_config_4_to_5_incremental | 10 |
| before_fix_config_4_to_5_clean | 11 |
| after_fix_config_4_clean | 10 |
| after_fix_config_4_to_5_incremental | 11 |
| after_fix_config_5_to_6_incremental | 12 |
| after_fix_noop | 12 |
| restored_output | 12 |

原始命令、标准输出、错误输出与退出码见 commands.txt；完整元数据、目标文件哈希及时间戳见 observations.json。

此记录验证已知参考补丁及候选拒绝恢复流程，不是 MDFixer 自动修复输出或 BuildChecker 检测报告。此 Macro 案例只验证 DEPS 中 config.h 的 MD 修复，不含刻意加入的项目内 RD。

修复后两次只改头文件均自动重建；故意失败候选被拒绝，恢复后完整构建与功能检查通过。
