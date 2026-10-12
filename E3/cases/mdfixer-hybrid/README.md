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

## 盛浩宇负责的 Target 子案例（2026-10-12 迁入）

按照本成员目录安排，Target 直接声明案例放在 [target/](target/README.md)，包含 fixture、oracle、patches、scripts 和 evidence；当前目录的主 fixture 和脚本仍为 Hybrid。
Target 原始任务分支 `b08/e3-mdfixer-target` 已保留，本次新分支为 `b08/e3-mdfixer-hybrid-layout`，基于组长目录调整后的 main `d27dc4c`。

| Target 交付 | 入口 |
|---|---|
| 直接声明故障项目 | [target/fixture/](target/fixture/) |
| MD-only 固定输入 | [target/oracle/expected.json](target/oracle/expected.json) |
| 参考/无效 Patch | [reference.patch](target/patches/reference.patch)、[invalid.patch](target/patches/invalid.patch) |
| 执行脚本 | [target/scripts/run.py](target/scripts/run.py) |
| 原 44/44 实际证据 | [2026-10-11 记录](target/evidence/20261011T110959885929+0800/README.md) |

Target 规则直接声明 `src/main.c include/common.h`，参考补丁直接补入 config.h，不使用依赖变量，没有项目内 RD。原行为及 Patch 保持不变；迁移后固定 Fixture 提交为 `a03812e0ec7bd689762fdb18cdfc66a07ef7f954`，与旧版本的源码/Makefile 字节相同，仅来源和路径说明更新。

```bash
python3 E3/cases/mdfixer-hybrid/target/scripts/run.py --operator "姓名（本人发起复现）"
```

Hybrid 与 Target 的原成员确认分别保留 2026-10-09 和 2026-10-11 的真实日期，详情见 [REVIEW.md](REVIEW.md)。[Hybrid review.json](oracle/review.json) 与 [Target review.json](target/oracle/review.json) 绑定当时确认的原始 input/md-report.json 和 observations.json；当前 Oracle 单独记录哈希与迁移关系，不将新的 AI 运行写成人工执行。
原日志只移动位置，原始时间、路径、执行者、pending 和哈希全部保留。迁移映射见 [MIGRATION.md](MIGRATION.md)，提交步骤见 [MANUAL_STEPS.md](MANUAL_STEPS.md)。

## 迁移后的实际验收

2026-10-12 在 Ubuntu 24.04 WSL、x86_64、GCC 13.3.0、GNU Make 4.3、Python 3.12.3 下，由 Codex 执行新入口：

| 案例 | 检查结果 | 原始命令数 | 新证据 |
|---|---|---|---|
| Hybrid | 40/40 PASS | 39 | [运行 README](evidence/20261012T144643089037+0800/README.md)、[observations.json](evidence/20261012T144643089037+0800/observations.json) |
| Target | 44/44 PASS | 39 | [运行 README](target/evidence/20261012T144600994684+0800/README.md)、[observations.json](target/evidence/20261012T144600994684+0800/observations.json) |

两套案例均复现修复前增量旧值、修复后两次自动重编译、无效候选退出码 2、拒绝与精确恢复成功。新输入、脚本和源码哈希由新日志记录；原始故障源码保持不变。

迁移完整性核查见 [MIGRATION_VALIDATION.json](MIGRATION_VALIDATION.json)：44 个历史证据文件逐字节一致，两套新日志与 JSON/哈希相符，固定提交可由新分支历史取得，当前链接有效，PR 变更仅涉及本成员目录。
