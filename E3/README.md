# B08 E3：MDFixer Hybrid 与 Target 修复基线

盛浩宇（241250008）本次负责 Hybrid 文档收尾与 Target 直接声明案例。本目录提供两套可复现的固定输入、参考修复、失败候选以及 Linux 验证证据。
原 Hybrid 材料已通过 [PR #2](https://github.com/Delario17/DevOps-Course-Assignment/pull/2) 合并至 main；本次在其基础上增加 Target。

## 交付入口

| 材料 | Hybrid 混合声明 | Target 直接声明 |
|---|---|---|
| 故障项目及来源 | [fixtures/mdfixer-hybrid/](fixtures/mdfixer-hybrid/) | [fixtures/mdfixer-target/](fixtures/mdfixer-target/) |
| 固定样例提交 | `4f13da22499dbee5ad3b63360e5b8b0af1bfcf98` | `b2d5709275471d4264215f6d40bd4bdd3bbfdd8a` |
| MD-only 参考 Oracle | [expected.json](oracle/mdfixer-hybrid.expected.json) | [expected.json](oracle/mdfixer-target.expected.json) |
| 当前审阅状态及输入哈希 | [review.json](oracle/mdfixer-hybrid.review.json) | [review.json](oracle/mdfixer-target.review.json) |
| 参考补丁 | [reference.patch](patches/mdfixer-hybrid.reference.patch) | [reference.patch](patches/mdfixer-target.reference.patch) |
| 无效补丁 | [invalid.patch](patches/mdfixer-hybrid.invalid.patch) | [invalid.patch](patches/mdfixer-target.invalid.patch) |
| 独立执行脚本 | [run_mdfixer_hybrid.py](scripts/run_mdfixer_hybrid.py) | [run_mdfixer_target.py](scripts/run_mdfixer_target.py) |
| 主要实际证据 | [本人复现记录](evidence/mdfixer-hybrid/20261009T133714630641+0800/README.md) | [Codex 执行记录](evidence/mdfixer-target/20261011T110959885929+0800/README.md) |
| 当前技术验收 | 40/40 PASS，39 条命令 | 44/44 PASS，39 条命令 |
| 当前成员确认 | 已确认，2026-10-09 | 待成员阅读确认 |

Target 的说明及验收清单见 [TARGET_README.md](TARGET_README.md)。本人操作见 [MANUAL_STEPS.md](MANUAL_STEPS.md)；贡献、AI 使用和人工确认分别见 [CONTRIBUTIONS.md](CONTRIBUTIONS.md)、[AI_USAGE.md](AI_USAGE.md)、[HUMAN_REVIEW.md](HUMAN_REVIEW.md)。

## 两种声明的区别

Hybrid 原规则为 `build/main.o: src/main.c $(HEADERS)`，直接文件与依赖变量混合；HEADERS 漏掉 config.h，额外保留 unused.h。补丁只补 MD，既有 RD 保留。
Target 原规则为 `build/main.o: src/main.c include/common.h`，依赖全部写成直接文件名；补丁直接在目标行补上 include/config.h，没有项目内 RD。CC/CFLAGS 等编译选项变量不影响依赖声明分类。Target 对应 E2 枚举 `DEPENDENCY_LIST`。

## 已观察的行为

| 阶段 | Hybrid | Target |
|---|---|---|
| 初始 CONFIG_VALUE=4，完整构建 | 10 | 10 |
| 修复前只改 4→5，普通构建 | 仍为 10，产物未更新 | 仍为 10，产物未更新 |
| 相同源码 clean 后重新构建 | 11 | 11 |
| 修复后恢复 4，完整构建 | 10 | 10 |
| 修复后只改 4→5，不 clean | 自动重编译，11 | 自动重编译，11 |
| 修复后只改 5→6，不 clean | 自动重编译，12 | 自动重编译，12 |
| 加入 false 的无效候选 | 退出码 2，REJECTED | 退出码 2，REJECTED |
| 恢复上一份有效 Makefile | 字节一致，重建输出 12 | 字节一致，重建输出 12 |

环境：Ubuntu 24.04 WSL、x86_64、GCC 13.3.0、GNU Make 4.3、Python 3.12.3。配置标识分别为 `b08-hybrid-74f06528d5480265` 和 `b08-target-74f06528d5480265`；源码版本独立记录。此执行未使用 Docker 镜像。

## Linux 执行

从仓库根目录运行，需要 python3、gcc、make、git，无需 pip 安装：

```bash
python3 E3/scripts/run_mdfixer_hybrid.py --operator "姓名（本人发起脚本复现）"
python3 E3/scripts/run_mdfixer_target.py --operator "姓名（本人发起脚本复现）"
```

脚本核对固定提交的源码后，在 Linux 临时目录构建、应用补丁及恢复；故障 Fixture 保持原样。每次生成独立时间目录，不覆盖旧证据。
参考补丁从原始 Makefile 应用；无效补丁从已接受的参考 Makefile 应用；应用位置均为临时样例根目录。

## Hybrid 状态收尾

旧 Oracle、SOURCE.md、运行 README 和 observations.json 的 pending 是准备或执行时的快照。随后完成的个人确认见 HUMAN_REVIEW.md。
本次新增 review.json，绑定原 Oracle 和个人复现 observations.json 的 SHA-256，作为当前审阅状态入口；原始文件和 2026-10-09 三次运行证据均保持字节不变。
因此“已确认”的当前状态与历史 pending 有明确时间顺序，旧输入哈希与实验溯源仍然成立。

## 组内衔接

本交付是 E3 测试基线：验证已知参考补丁，不代表 MDFixer 自动修复服务已实现。Oracle 是注明 AI 辅助来源的参考输入；ACCEPTED/REJECTED 为脚本实验决定，不作为真实检测服务/API Job 输出。
DRAFT 由王祎负责，Macro 及统一验证入口由朱雨乐负责，Implicit 与最终组级材料由孙博一负责。本次提供两个独立脚本供统一入口调用，最终四人贡献表与总验收由组内汇总。
