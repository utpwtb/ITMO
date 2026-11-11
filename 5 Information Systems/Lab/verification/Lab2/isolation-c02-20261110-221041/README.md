# C02 事务隔离级别对照

对应实验第 4 项。在 Helios 上用 10 个线程跑 20 轮，每轮同时创建同名、同导演的电影。测试期望每轮恰好一个 `201`、九个 `409 DUPLICATE_MOVIE`，并确认数据库只新增一部电影。

| 隔离级别 | 最多尝试 | 201 | 409 | 503 | 自动重试 | C02 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| READ COMMITTED | 3 | 20 | 180 | 0 | 0 | 通过 |
| SERIALIZABLE | 3 | 20 | 180 | 0 | 98 | 通过 |
| SERIALIZABLE | 1 | 20 | 89 | 91 | 0 | 失败 |
| READ COMMITTED | 1 | 20 | 180 | 0 | 0 | 通过 |

四组均跑满 20 轮，数据库每轮只保存一部电影。单次尝试的失败组可以看 [HTTP 503](single-serializable/C02/responses.jsonl) 和 [后端日志](single-serializable/server.log)。Payara 日志记录 PostgreSQL 的并发更新错误，同一锁语句另用 psql 重现并记录了 [SQLSTATE 40001](sqlstate-probe.log)。切换后的结果见 [通过断言](single-read-committed/C02/assertions.json)。

## 在 Helios 复跑

```bash
cd /home/studs/s407960/is-lab2-4101
python3.11 verification/Lab2/run-isolation-c02.py "isolation-c02-$(date +%Y%m%d-%H%M%S)"
```

脚本在测试端口 `40801` 启动同一份 WAR。对照专用 JMX 的第 16 行设置为 `continue`，使样本失败后继续测满 20 轮。四组都用同一份 JMX，断言仍把 `503` 算作失败。先在默认的三次事务尝试下比较两个隔离级别，再把两组都固定为一次尝试。

组间只清理刚生成的测试电影、导演和坐标，随后核对六张测试表的数据行指纹。序列和 `AppState.revision` 按正常写入递增。正式应用继续监听 `40797`。

服务器的新结果位于项目的 `verification/Lab2/isolation-c02-<时间>/`。每组目录里有 `C02/html/index.html`、`C02/results.jtl`、`C02/responses.jsonl`、`C02/assertions.json`、`server.log` 和 `run-statistics.json`。

[答辩逐步操作与中俄讲稿](../../../defense/Lab2/实验二答辩演示脚本.md)
