# E3 MDFixer HYBRID 修复基线与验证证据

新增一套 B08 HYBRID 声明风格的 MDFixer 测试基线。项目读取 `config.h`，原 Makefile 的 `HEADERS` 遗漏该文件；修复前仅修改配置值时，增量构建仍输出旧值 10，完整重建输出 11。参考补丁补上 `config.h` 后，两次头文件单独变更均自动重编译，输出依次为 11 和 12。

案例材料统一位于 `E3/cases/mdfixer-hybrid/`，包含注明 A08 归属的故障项目、MD-only Oracle、参考补丁、失败候选、验证与恢复脚本、运行日志和个人记录。失败候选构建退出码为 2，拒绝后恢复上一份有效 Makefile，重新构建输出 12。

Codex 在 Ubuntu 24.04 WSL、GCC 13.3.0、GNU Make 4.3、Python 3.12.3 环境完成最终脚本验证，40/40 PASS。固定样例提交为 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`，最终脚本证据位于 `E3/cases/mdfixer-hybrid/evidence/20261009T123645645063+0800/`。

盛浩宇（241250008，`lejuwujiang258`）于 2026-10-09 发起个人复现，40/40 PASS，39 条命令已记录；个人证据位于 `E3/cases/mdfixer-hybrid/evidence/20261009T133714630641+0800/`，证据提交为 `e9e59b6a017d179ba5e845203c1665ad8450cf37`。
