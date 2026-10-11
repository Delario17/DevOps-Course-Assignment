# DevOps Course Assignment

本仓库用于 B08 小组的 DevOps 课程实验。

## E2：需求与接口契约

- 作业说明：[`E2/README.md`](E2/README.md)
- 接口契约：[`E2/INTERFACE_CONTRACT.md`](E2/INTERFACE_CONTRACT.md)
- OpenAPI：[`E2/openapi.yaml`](E2/openapi.yaml)
- A08 配对评审：[`E2/A08_REVIEW.md`](E2/A08_REVIEW.md)
- 个人贡献：[`E2/CONTRIBUTIONS.md`](E2/CONTRIBUTIONS.md)

从仓库根目录执行验收：

```bash
python3 -m pip install -r E2/requirements.txt
python3 E2/validate.py
```

契约版本 `1.0.0` 已于 2026-09-20 通过 A08 配对评审，评审结论为“通过，无必须修改项”。

## E3：MDFixer Hybrid 与 Target 修复基线

- 案例与实际结果：[`E3/README.md`](E3/README.md)。
- Target 说明与验收：[`E3/TARGET_README.md`](E3/TARGET_README.md)。
- 本人重跑、审阅和提交步骤：[`E3/MANUAL_STEPS.md`](E3/MANUAL_STEPS.md)。
- 贡献认领：[`E3/CONTRIBUTIONS.md`](E3/CONTRIBUTIONS.md)。
- 当前成员确认：[`E3/HUMAN_REVIEW.md`](E3/HUMAN_REVIEW.md)。

原 Hybrid 已通过 PR #2 合并，个人复现和确认已记录，40/40 通过。本次盛浩宇的分工新增 Target 直接声明案例，Codex Linux 实际执行 44/44 通过，盛浩宇已阅读并单独确认辅助核查结论；当前审阅状态以 E3/HUMAN_REVIEW.md 和各案例 review.json 为准。DRAFT、Macro、Implicit 及最终汇总按组内分工整合。
