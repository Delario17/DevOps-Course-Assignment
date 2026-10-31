# B-draft 云主机实验

本目录是可运行的教学参考实现，已合并 E6/E7 代码，未包含助教门禁演示测试。
请先阅读实验包 docs/00_开始与目录.md，再按 03_B轨道操作指南.md 完成步骤。
统一入口：`python3 scripts/lab_cloud.py --help`。
不需要 Windows、WSL、Docker Desktop，不使用助教的学号、代理地址或宿主机目录。
仓库旧 Makefile/Compose 属于 E4 环境接口；本次优先使用 lab_cloud.py，避免镜像标签混用。

B08 E5 从本目录执行。
运行前先 cd E5。

本组使用标称 2 GiB ECS，最低可见内存检查调整为 1.5 GiB。
原始证据位于 work/，报告位于 docs/。