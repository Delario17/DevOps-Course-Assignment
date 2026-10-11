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

## E3：并行测试基线

- 总览与实际结果：[`E3/README.md`](E3/README.md)。
- DRAFT Tiny Greeting：[`E3/DRAFT_BASELINE.md`](E3/DRAFT_BASELINE.md)。
- 本人重跑、审阅和提交步骤：[`E3/MANUAL_STEPS.md`](E3/MANUAL_STEPS.md)。
- 贡献认领：[`E3/CONTRIBUTIONS.md`](E3/CONTRIBUTIONS.md)。

MDFixer HYBRID 案例已完成 40/40 Linux 复现与人工确认。DRAFT Tiny Greeting 已完成固定项目、失败与参考环境、Oracle 和自动验证脚本；本机构建与功能验证为 18/18 通过，Docker 最终复现待完成。
