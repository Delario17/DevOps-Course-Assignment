# E3 MDFixer IMPLICIT 隐式规则修复基线

新增独立的 `E3/cases/mdfixer-implicit/` 案例。故障 Makefile 使用
`build/%.o: src/%.c` 模式规则，但漏掉源码实际包含的 `include/config.h`。
参考补丁把头文件补到模式规则，并通过可重复的 Linux 实验验证修复前陈旧构建、
修复后连续增量重编译、失败候选拒绝和精确回滚。

本案例包含固定 fixture、SHA-256 Oracle、参考及无效补丁、验证脚本、运行证据和独立贡献记录。
它验证参考修复流程，不声称 MDFixer 服务已经实现。人工复现和确认仍按 `REVIEW.md` 如实记录。
