# B08 E3：MDFixer HYBRID 基线

## 核心设计

目标规则 `build/main.o: src/main.c $(HEADERS)` 同时包含直接文件项和变量展开项，因此归类为 HYBRID。原 Makefile 的 `HEADERS` 遗漏 `include/config.h`，又额外声明 `include/unused.h`。本案例用“参考补丁修复 MD、保留既有 RD”分离两类问题，再通过两次头文件单独变更检验增量重建行为。

## 案例产物

| 内容 | 位置 |
|---|---|
| 固定故障项目与 A08 来源 | [`fixture/`](fixture/) |
| MD-only 参考输入及预期 | [`oracle/expected.json`](oracle/expected.json) |
| 参考修复 | [`patches/reference.patch`](patches/reference.patch) |
| 故意失败候选 | [`patches/invalid.patch`](patches/invalid.patch) |
| 行为验证与恢复脚本 | [`scripts/run.py`](scripts/run.py) |
| 历史运行证据 | [`evidence/`](evidence/) |
| 个人贡献与 AI 使用 | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md)、[`AI_USAGE.md`](AI_USAGE.md) |
| 复现与审阅 | [`MANUAL_STEPS.md`](MANUAL_STEPS.md)、[`REVIEW.md`](REVIEW.md) |
| PR 说明 | [`PR_DESCRIPTION.md`](PR_DESCRIPTION.md) |

固定样例位于 B08 提交 `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98`，A08 源码归属与参考版本见 [`fixture/SOURCE.md`](fixture/SOURCE.md)。固定提交中的样例路径为 `E3/fixtures/mdfixer-hybrid/`，当前路径为 `E3/cases/mdfixer-hybrid/fixture/`。

## 成功标准与实测结果

| 阶段 | 预期 | 2026-10-09 实际结果 |
|---|---|---|
| 初始完整构建，`CONFIG_VALUE=4` | 10 | 10 |
| 修复前改为 5，增量构建 | 保持 10 | 10 |
| 相同源码完整重建 | 11 | 11 |
| 参考修复后恢复 4，完整构建 | 10 | 10 |
| 修复后改为 5，增量构建 | 重编译并输出 11 | 11 |
| 修复后改为 6，增量构建 | 再次重编译并输出 12 | 12 |
| 应用失败候选 | 非零退出并拒绝 | 退出码 2，REJECTED |
| 恢复有效 Makefile | 字节一致，构建与运行通过 | 输出 12，PASSED |

最终脚本验证与盛浩宇个人复现均为 40/40 PASS，每次记录 39 条命令。实测环境为 Ubuntu 24.04 WSL、x86_64、GCC 13.3.0、GNU Make 4.3 和 Python 3.12.3，配置标识为 `b08-hybrid-74f06528d5480265`。个人复现证据位于 [`evidence/20261009T133714630641+0800/`](evidence/20261009T133714630641+0800/)。

## Linux 复现

在仓库根目录执行：

```bash
python3 E3/cases/mdfixer-hybrid/scripts/run.py --operator "姓名（本人发起复现）"
```

脚本将 fixture 复制到 Linux 临时目录完成补丁实验，原始故障样例保持不变；新证据按时间写入 `evidence/`。
