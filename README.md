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

E3 用固定输入提交、Oracle、验证脚本和原始 evidence 组成可复现证据链，覆盖 DRAFT 环境生成基线及四种 MDFixer 依赖声明风格。

| 案例 | 入口 | 已保存结果 |
|---|---|---|
| DRAFT Tiny Greeting | [`E3/cases/draft-tiny-greeting/`](E3/cases/draft-tiny-greeting/README.md) | 王祎本人 Docker 复现，24/24 PASS |
| MDFixer TARGET | [`E3/cases/mdfixer-target/`](E3/cases/mdfixer-target/README.md) | 44/44 PASS，盛浩宇确认核查结论 |
| MDFixer MACRO | [`E3/cases/mdfixer-macro/`](E3/cases/mdfixer-macro/README.md) | 46/46 PASS；四类统一入口 164/164 PASS |
| MDFixer HYBRID | [`E3/cases/mdfixer-hybrid/`](E3/cases/mdfixer-hybrid/README.md) | 盛浩宇本人 Linux 复现，40/40 PASS |
| MDFixer IMPLICIT | [`E3/cases/mdfixer-implicit/`](E3/cases/mdfixer-implicit/README.md) | 34/34 PASS，孙博一本人确认待补 |

- 总览、复现命令与作业要求映射：[`E3/README.md`](E3/README.md)
- 组级贡献索引：[`E3/CONTRIBUTIONS.md`](E3/CONTRIBUTIONS.md)
- AI 使用索引：[`E3/AI_USAGE.md`](E3/AI_USAGE.md)

在 Linux/Ubuntu WSL 中从仓库根目录执行四类 MDFixer 统一验证：

```bash
python3 E3/cases/mdfixer-macro/scripts/run_mdfixer_all.py \
  --operator "实际执行者"
```
