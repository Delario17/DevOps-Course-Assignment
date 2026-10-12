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

- 总览与案例目录契约：[`E3/README.md`](E3/README.md)。
- DRAFT Tiny Greeting：[`E3/cases/draft-tiny-greeting/`](E3/cases/draft-tiny-greeting/README.md)。
- MDFixer HYBRID：[`E3/cases/mdfixer-hybrid/`](E3/cases/mdfixer-hybrid/README.md)。
- 组级贡献与 AI 使用索引：[`E3/CONTRIBUTIONS.md`](E3/CONTRIBUTIONS.md)、[`E3/AI_USAGE.md`](E3/AI_USAGE.md)。

MDFixer HYBRID 案例已完成 40/40 Linux 复现与人工确认。DRAFT Tiny Greeting 由王祎本人发起完整 Docker 复现，24/24 项断言通过。两套基线的 fixture、Oracle、脚本、evidence 和个人文档均收拢到各自的案例目录。
