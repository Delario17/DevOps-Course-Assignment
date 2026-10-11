# MDFixer Target 直接声明故障样例

本目录保留未修复的 Makefile，供验证脚本复制到临时目录测试。main.c 实际读取 common.h 和 config.h；目标依赖只直接声明 main.c 和 common.h，故意遗漏 config.h。

构建及功能验证命令（只在自己的样例副本中执行）：

```bash
make clean
make -j2
./bin/demo --version
./bin/demo
```

初始版本输出 demo 1.0.0，数值输出 10。源码来源和范围见 SOURCE.md。
推荐从仓库根目录运行 `python3 E3/scripts/run_mdfixer_target.py --operator "实际执行者"`，自动保留每次新证据，避免直接修改本目录。
Patch 中的 a/Makefile 和 b/Makefile 相对于临时样例根目录；不要在仓库根目录直接应用这些补丁。
