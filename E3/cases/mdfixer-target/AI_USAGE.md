# MDFixer TARGET AI 使用记录

- 工具：Codex。
- 日期：2026-10-11 至 2026-10-12，Asia/Shanghai。
- 任务：建立 TARGET 直接声明案例，完成参考补丁、失败候选、增量重建与恢复验证。
- 来源：C 源码和头文件复用 A08 参考版本 `f8584a58e7be9d39ca630b5c6617a9ed25e8e4da`，归属见 [`fixture/SOURCE.md`](fixture/SOURCE.md)。
- AI 编写：直接声明 Makefile、MD-only Oracle、参考与无效补丁、Linux 验证脚本和案例文档。
- AI 执行：Ubuntu 24.04 WSL、GCC 13.3.0、GNU Make 4.3、Python 3.12.3；两次运行均为 44/44 PASS。
- 关键结果：修复前头文件变更保留旧值 10；参考修复后两次增量输出 11 和 12；失败候选退出码 2，恢复后输出 12。
- 证据核对：Codex 核对 fixture、Oracle、补丁、39 条命令、阶段输出和恢复字节。
- 成员确认：盛浩宇于 2026-10-11 阅读并确认辅助核查结论。
