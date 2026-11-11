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

## 地点唯一性版本 · 2026-11-10

新版先在 Helios 构建并通过 143 项测试，集成测试使用 `lab2_loc_261110_` 表前缀。测试实例上的新增、重复新增和重复编辑分别返回 `201`、`409 DUPLICATE_LOCATION`、`409 DUPLICATE_LOCATION`。 [构建与测试日志](location-20261110/server-verify.log) · [HTTP 检查](location-20261110/location-http.json)

C01、C02、C03 各跑 20 轮，280 次目标请求中有 60 次提交、220 次预期拒绝，非预期失败为 0。更新后的 C03 每份获胜文件各新增两部电影、两条坐标、两个人物和两个地点，失败批次残留为 0。 [JMeter 汇总](location-20261110/jmeter/summary.json) · [C03 断言](location-20261110/jmeter/C03/assertions.json)

正式实例 `movies-helios` 已切换到新版，部署时 PID 为 `15236`。正式库各表行数与切换前相同，旧库的一组重复地点仍保留。旧 WAR 备份在服务器项目目录的 `.runtime/location-deploy-20261110/backup/movie-lab.war`。 [部署记录与 WAR 校验值](location-20261110/deployment.json)
