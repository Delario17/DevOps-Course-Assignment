# MDFixer IMPLICIT 隐式规则修复基线

本案例独立验证 GNU Make 模式规则中的缺失依赖修复。故障规则
`build/%.o: src/%.c` 会编译实际包含 `include/config.h` 的源码，却没有声明该头文件，
导致只修改配置头文件时保留陈旧产物。

参考补丁把 `include/config.h` 加入模式规则。验证脚本覆盖：

- 修复前头文件变更不会触发增量重编译，输出错误地保持为 `10`；
- 相同源码干净重建后输出 `11`；
- 修复后连续两次头文件变更均触发重编译，输出依次为 `11`、`12`；
- 故意插入 `false` 的候选构建失败并被拒绝；
- 恢复最后接受的 Makefile 后构建和功能输出通过。

## 目录

| 内容 | 路径 |
|---|---|
| 固定故障输入 | `fixture/` |
| Oracle 与 SHA-256 清单 | `oracle/expected.json` |
| 参考及无效补丁 | `patches/` |
| Linux 验证脚本 | `scripts/run.py` |
| 实际运行记录 | `evidence/` |

## 重跑

从仓库根目录在 Linux/WSL 中执行：

```bash
python3 E3/cases/mdfixer-implicit/scripts/run.py --operator "姓名（本人发起复现）"
```

脚本只在临时目录应用补丁，每次创建新的证据目录，不修改固定 fixture。
该流程验证已知参考补丁，不是 MDFixer 或 BuildChecker 服务输出。
