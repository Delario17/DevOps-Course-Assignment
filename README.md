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

## E3：MDFixer HYBRID 修复基线

- 案例与实际结果：[`E3/README.md`](E3/README.md)。
- 本人重跑、审阅和提交步骤：[`E3/MANUAL_STEPS.md`](E3/MANUAL_STEPS.md)。
- 贡献认领：[`E3/CONTRIBUTIONS.md`](E3/CONTRIBUTIONS.md)。

此交付包含 HYBRID 和 IMPLICIT 声明风格的参考修复案例。HYBRID 的 Codex 验证与盛浩宇本人发起的 Linux 复现均为 40/40 通过；本人已阅读并确认辅助核查结论与运行结果一致，记录见 E3/HUMAN_REVIEW.md。IMPLICIT 案例提供独立的固定输入、补丁和 Linux 验证脚本。DRAFT 和其他声明风格由 B08 组内继续协调。
