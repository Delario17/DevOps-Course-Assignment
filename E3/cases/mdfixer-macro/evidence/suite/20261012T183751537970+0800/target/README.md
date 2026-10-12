# MDFixer TARGET 实际运行记录

- 执行时间：2026-10-12T18:37:51.770758+08:00。
- 实际执行者：Codex automated verification after owned-case migration; human reading confirmation not recorded。
- 固定样例提交：`a03812e0ec7bd689762fdb18cdfc66a07ef7f954`。
- 运行时仓库提交：`83354f218a03a2085b4e571582f8d333d3a4ddf3`。
- 配置标识：`b08-target-85c0951fe9a1432f`。
- 结果：**PASS**，44/44 项断言通过。
- 人工审阅：待实际 B08 成员确认。

| 实验阶段 | 实际输出 |
|---|---|
| initial | 10 |
| before_fix_config_4_to_5_incremental | 10 |
| before_fix_config_4_to_5_clean | 11 |
| after_fix_config_4_clean | 10 |
| after_fix_config_4_to_5_incremental | 11 |
| after_fix_config_5_to_6_incremental | 12 |
| restored_output | 12 |

原始命令、标准输出、错误输出与退出码见 commands.txt；完整元数据、目标文件哈希及时间戳见 observations.json。

此记录验证已知参考补丁及候选拒绝恢复流程，不是 MDFixer 自动修复输出或 BuildChecker 检测报告。本案例没有项目内 RD，只验证直接声明 config.h 的 MD 修复。

修复后两次只改头文件均自动重建；故意失败候选被拒绝，恢复后完整构建与功能检查通过。
