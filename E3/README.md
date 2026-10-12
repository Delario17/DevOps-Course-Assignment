# B08 E3：并行测试基线

E3 以“一个案例对应一条完整证据链”为组织原则。每个案例将固定输入、Oracle、补丁、验证脚本、运行证据和个人记录收拢到 `E3/cases/<case>/`，使各成员可在独立分支中完成一个案例，合并时只由集成负责人更新本页及组级索引。

## 案例状态

| 案例 | 类型 | 结果 | 入口 |
|---|---|---|---|
| DRAFT Tiny Greeting | 环境生成基线 | 王祎本人发起 Docker 复现，24/24 PASS | [`cases/draft-tiny-greeting/`](cases/draft-tiny-greeting/README.md) |
| MDFixer HYBRID | 混合声明修复基线 | 盛浩宇本人发起 Linux 复现，40/40 PASS | [`cases/mdfixer-hybrid/`](cases/mdfixer-hybrid/README.md) |

MDFixer TARGET、MACRO 和 IMPLICIT 案例在各自任务分支中以同样的目录规则完成，集成后加入上表。

## 单案例目录契约

```text
E3/cases/<case>/
├── README.md
├── CONTRIBUTIONS.md
├── AI_USAGE.md
├── REVIEW.md
├── MANUAL_STEPS.md        # 需要人工复现说明时提供
├── PR_DESCRIPTION.md
├── fixture/
├── oracle/
├── patches/               # MDFixer 案例使用
├── scripts/
└── evidence/
```

`README.md` 说明案例动机、判据和实测结果；`CONTRIBUTIONS.md` 和 `AI_USAGE.md` 仅记录该案例；`evidence/` 按运行时间建立新目录，保留每次实验快照。

## 协作边界

案例负责人只修改 `E3/cases/<case>/` 下的文件。`E3/README.md`、`E3/CONTRIBUTIONS.md` 和 `E3/AI_USAGE.md` 是组级索引，在集成分支中统一更新。这一边界使成员分支的 Git 变更集不重叠，同时保持每个案例的证据可独立审查。

本次迁移仅改变历史 `evidence/` 文件的仓库位置，文件内容和哈希保持不变。历史命令日志中的旧路径是实验当时的原始记录。

## 复现入口

```bash
python3 E3/cases/draft-tiny-greeting/scripts/run.py --operator "姓名" --docker required
python3 E3/cases/mdfixer-hybrid/scripts/run.py --operator "姓名（本人发起复现）"
```

DRAFT 脚本支持 Linux 和 Docker Desktop；MDFixer HYBRID 脚本使用 Linux/WSL 工具链。
