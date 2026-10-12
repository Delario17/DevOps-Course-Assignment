# 朱雨乐：MDFixer Macro 声明基线与统一验证入口

负责人：朱雨乐，241250011。个人分支：`b08/e3-mdfixer-macro-layout`。所有本次交付、忽略规则和后续运行证据位于 `E3/cases/mdfixer-macro/`。

| 内容 | 本目录路径 |
|---|---|
| 固定故障项目与来源 | `fixture/`、`fixture/SOURCE.md` |
| 人工 MD 输入与行为预期 | `oracle/expected.json` |
| 参考修复、失败候选 | `patches/reference.patch`、`patches/invalid.patch` |
| Macro 验证 | `scripts/run.py` |
| MDFixer 四类统一入口 | `scripts/run_mdfixer_all.py` |
| 入口行为测试 | `tests/test_suite_entrypoint.py` |
| 历史 AI 运行和本人复现 | `evidence/history/` |
| 迁移追溯与校验 | `MIGRATION.md`、`HISTORY_MANIFEST.json` |
| 个人贡献、AI 使用、复现记录 | `CONTRIBUTIONS.md`、`AI_USAGE.md`、`REVIEW.md` |

原规则为 `build/main.o: $(DEPS)`，宏为 `DEPS := src/main.c include/common.h`。main.c 还读取 config.h，遗漏它导致头文件变更无法触发增量重建。参考补丁只在 DEPS 添加 `include/config.h`，保留目标规则和 recipe，符合课件的纯 Macro 风格。

本目录 Fixture 固定提交为 `83354f218a03a2085b4e571582f8d333d3a4ddf3`；验证器逐文件对照该提交的 Git blob。请保留此提交历史。来源为已有注明 A08 归属的 B08 样例，C 源码和行为保持不变。

| 阶段 | 预期输出/判据 |
|---|---|
| 初始 CONFIG_VALUE=4 | 10 |
| 修复前 4→5，仅 make | 仍为 10，产物不变 |
| 相同源码 clean 重建 | 11 |
| 参考修复后恢复 4、clean 构建 | 10 |
| 修复后 4→5，不 clean | 自动重编译，11 |
| 修复后 5→6，不 clean | 再次自动重编译，12 |
| 无修改再次 make | 12，产物不变 |
| 加入 false 的失败候选 | 构建退出码非零，REJECTED |
| 恢复候选应用前的有效 Makefile | 字节一致，构建运行输出 12 |

项目版本、Oracle 和实际观察分别保存。本案例验证已知参考补丁和拒绝恢复流程，未声称已实现自动 MDFixer 或生成真实 BuildChecker 报告。构建在 Linux 临时副本中完成，仓库故障 Fixture 保持原样。

从仓库根目录在 Linux/Ubuntu WSL 执行，需要 python3、gcc、GNU Make、git：

```bash
python3 E3/cases/mdfixer-macro/scripts/run.py --operator "实际执行者"
python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py --operator "实际执行者"
python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py --cases macro --operator "实际执行者"
python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py --cases available --operator "实际执行者"
python3 -m unittest discover -s E3/cases/mdfixer-macro/tests -v
```

Windows PowerShell：

```powershell
wsl -d Ubuntu --cd /mnt/d/Devops/DevOps-Course-Assignment --exec python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py --operator "朱雨乐（本人发起复现）"
```

统一入口默认要求 Target、Macro、Hybrid、Implicit 齐全且通过。兼容 Target 当前位于 `../mdfixer-hybrid/target/` 的布局和未来独立 `../mdfixer-target/`。单个缺失或失败仍保存其他案例证据，最终返回非零；部分案例通过使用 `PASS_SELECTED`，四类全部通过才使用 `PASS`。

新 Macro 输出到本目录 `evidence/macro/时间/`，统一入口输出到 `evidence/suite/时间/`。所有 `--output` 必须是本目录 `evidence/` 或 `.runs/` 下的新子目录，拒绝向公共目录、其他案例或 Fixture 写入。统一入口传递该输出路径给成员脚本，不把日志写回其案例目录。

## 保留的历史证据

- [2026-10-11 首轮 Macro+Hybrid](evidence/history/20261011T190636028688+0800/README.md)：Macro 46/46、Hybrid 40/40。
- [四类固定输入兼容性](evidence/history/20261011T190635803060+0800-compatibility/README.md)：164/164；其他成员原固定版本见同目录 peer-refs.json。
- [朱雨乐本人发起复现](evidence/history/20261011T202758890990+0800/README.md)：Macro 46/46、Hybrid 40/40，退出码 0，81 条命令经 Codex 辅助核对。

107 个历史证据文件来自 `54ee1af68a9801cf723315b0c1efe3cddd4772e1`，字节及哈希不变。原始 README、命令和 JSON 中的旧路径、SHA、operator 与审阅状态保持当时记录；原路径与新路径对应见 HISTORY_MANIFEST.json。

## 协作与提交范围

本分支从当前 main 创建，只新增 `E3/cases/mdfixer-macro/`。公共 README、组级贡献/AI 文件、根 .gitignore 和其他成员目录均无差异。整合负责人只需合入本分支，并维护组级索引。

本目录 .gitignore 排除 .work/、.runs/、Fixture 的 build/bin、编译产物、Python 缓存、环境文件和常见密钥；正式 evidence 内的文本、JSON、Patch 才作为证据提交。单独的人工审阅签字不是课件必交材料，REVIEW.md 按实际记录本人复现和辅助核查。

## 迁移后实际验证（2026-10-12）

[本次完整运行](evidence/suite/20261012T183751537970+0800/README.md)由 Codex 在现有 Ubuntu 26.04 WSL、GCC 15.2.0、GNU Make 4.4.1、Python 3.14.4 执行，Target 44/44、Macro 46/46、Hybrid 40/40、Implicit 34/34，共 164/164 PASS。运行时提交为 Fixture 基线 `83354f218a03a2085b4e571582f8d333d3a4ddf3`，当次脚本与 Oracle 的 SHA-256 已记录在各子目录 observations.json 中。

入口测试 12/12 通过，涵盖嵌套/独立 Target、全部/部分/缺失/失败案例、异常证据、旧结果保护、默认输出归属和拒绝写入其他成员目录。107 个历史文件逐个对照原提交验证，字节保持不变；所有 Git 变更路径只位于本目录。核查摘要见 `MIGRATION_VALIDATION.json`。
