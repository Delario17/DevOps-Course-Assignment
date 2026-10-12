# B08 E3：并行测试基线

E3 的核心机制是把每个实验案例封装为一条可独立复现、可按哈希审计的证据链：固定输入提交定义测试对象，Oracle 定义判据，验证脚本在临时副本中执行失败—修复—拒绝—恢复流程，`evidence/` 保存原始命令与观察结果。五个案例因此可以并行开发，并在合入后由统一入口复核四种 Makefile 依赖声明风格。

## 交付状态

| 案例 | 负责人 | 核心判据 | 已保存结果 | 审阅状态 |
|---|---|---|---|---|
| [DRAFT Tiny Greeting](cases/draft-tiny-greeting/README.md) | 王祎（241250007） | 同一 Debian 基础镜像下，缺失工具链的构建失败，参考环境完成构建和功能验证 | 本人 Docker 复现，24/24 PASS | 已确认 |
| [MDFixer TARGET](cases/mdfixer-target/README.md) | 盛浩宇（241250008） | 直接文件依赖列表补入 `include/config.h` | Codex Linux 验证，44/44 PASS | 盛浩宇已确认核查结论 |
| [MDFixer MACRO](cases/mdfixer-macro/README.md) | 朱雨乐（241250011） | `$(DEPS)` 宏补入 `include/config.h` | 本人发起 WSL 复现：Macro 46/46、Hybrid 40/40；统一四类验证 164/164 PASS | 本人复现已记录 |
| [MDFixer HYBRID](cases/mdfixer-hybrid/README.md) | 盛浩宇（241250008） | 直接源文件与 `$(HEADERS)` 混合规则补齐 `config.h`，保留既有 RD | 本人 Linux 复现，40/40 PASS | 已确认 |
| [MDFixer IMPLICIT](cases/mdfixer-implicit/README.md) | 孙博一（241250078） | 模式规则 `build/%.o` 补入 `include/config.h` | Codex Linux 验证，34/34 PASS | 本人复现与确认待补 |

四种 MDFixer 风格均覆盖同一行为链：修复前只改头文件时产物陈旧，完整重建暴露正确输出；应用参考补丁后连续两次头文件变更均触发增量重编译；故意失败的候选补丁被拒绝，恢复后构建与功能检查通过。

## 目录契约

```text
E3/
├── README.md
├── CONTRIBUTIONS.md
├── AI_USAGE.md
├── integration-history/
└── cases/
    ├── draft-tiny-greeting/
    ├── mdfixer-target/
    ├── mdfixer-macro/
    ├── mdfixer-hybrid/
    └── mdfixer-implicit/
```

每个案例将 `fixture/`、`oracle/`、`scripts/`、`evidence/` 与成员记录放在同一目录，MDFixer 案例同时包含 `patches/`。成员分支只修改自己的案例目录，组级三个 Markdown 索引由集成分支统一更新。历史 evidence 中的旧路径、执行者、提交和审阅状态保持采集时原值；目录迁移映射见各案例的 `MIGRATION.md` 或历史清单。

## 复现入口

从仓库根目录执行：

```bash
# DRAFT：Docker Desktop 或 Linux Docker
python3 E3/cases/draft-tiny-greeting/scripts/run.py \
  --operator "实际执行者" --docker required

# MDFixer：Linux / Ubuntu WSL，需 python3、gcc、GNU Make、git
python3 E3/cases/mdfixer-target/scripts/run.py --operator "实际执行者"
python3 E3/cases/mdfixer-macro/scripts/run.py --operator "实际执行者"
python3 E3/cases/mdfixer-hybrid/scripts/run.py --operator "实际执行者"
python3 E3/cases/mdfixer-implicit/scripts/run.py --operator "实际执行者"

# 四种 MDFixer 风格统一验证
python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py \
  --operator "实际执行者"
```

每次运行创建新的时间戳证据目录，记录操作系统、工具版本、仓库提交、输入与脚本 SHA-256、命令标准输出/错误输出、退出码、阶段行为和恢复结果。

## 作业要求映射

| 课件要求 | 本仓库对应产物 |
|---|---|
| DRAFT 固定项目、构建与功能验证 | `cases/draft-tiny-greeting/fixture/`、`oracle/`、`scripts/` |
| 失败构建日志与成功参考环境 | DRAFT 最终 evidence 的 broken/reference 镜像记录 |
| 固定 MD 报告及对应 Makefile | 四个 MDFixer 案例的 `oracle/expected.json` 与 `fixture/Makefile` |
| Target、Macro、Hybrid、Implicit | 四个独立 `mdfixer-*` 案例目录 |
| 参考修复与行为复核 | 各案例 `patches/reference.patch`、运行脚本和 reference validation |
| 无效候选拒绝与恢复 | 各案例 `patches/invalid.patch`、rejected-candidate 与恢复断言 |
| 环境、仓库、SHA 和个人贡献 | evidence 元数据、`CONTRIBUTIONS.md`、`AI_USAGE.md` |

当前技术产物覆盖完整。正式提交前由孙博一运行 IMPLICIT 复现命令，并在 [`cases/mdfixer-implicit/REVIEW.md`](cases/mdfixer-implicit/REVIEW.md) 填写本人确认，即可补齐最后一项成员记录。
