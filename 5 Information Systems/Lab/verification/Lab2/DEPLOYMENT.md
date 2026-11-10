# Helios 部署与复跑

- SSH 使用 `s407960@helios.cs.ifmo.ru:2222`，项目在 `/home/studs/s407960/is-lab2-4101`。
- HTTP 监听 `127.0.0.1:40797/movie-lab/`，Hazelcast 内部监听 `127.0.0.1:40798`。持久化 Payara 配置重建时，应恢复回环地址和这两个端口。
- 2026-11-10 的验收使用当时运行的测试实例（PID 60635）。测试和正式实例分别使用 `lab2_4101_test_` 与 `lab2_4101_` 表，切换前请用 `python3.11 scripts/helios.py status` 确认状态。
- 本轮同步了精简后的 JMeter 运行器、测试计划、运行说明及报告。实际测试 WAR 的 SHA-256 是 `95cb5fe595aab5ccebd5cdef2917a7e2930d17cc91f0203947645710c341404e`。
- 新证据位于服务器项目目录的 `verification/Lab2/compact-20261110/`，报告位于 `report/Lab2/report.pdf`。[本轮配置](compact-20261110/configuration.json) · [本轮验收](ACCEPTANCE.md)

从 Windows 查看网页时，保持以下隧道运行。

```powershell
ssh -N -L 18083:127.0.0.1:40797 -o ExitOnForwardFailure=yes -p 2222 s407960@helios.cs.ifmo.ru
```

打开 [实验二网页](http://127.0.0.1:18083/movie-lab/)。应用启动和实例切换见 [项目 README](../../movie-lab/README.md)，并发场景复跑见 [JMeter README](../../movie-lab/jmeter/README.md)。
