# 实验二 Helios 验收

2026-11-10，在 Helios 的 `movies-helios-test` 实例和 `lab2_4101_test_` 表上执行。配置为显式 `READ COMMITTED`、`AppState` 写锁与客户端版本校验。JMeter 在服务器本机运行。下载的验收归档与服务器 SHA-256 一致，代码及 JMX 哈希也与本机文件一致。[运行配置](compact-20261110/configuration.json)

| 场景 | 线程 × 轮数 | 目标请求 | 成功写入 | 预期拒绝 | 数据库核对 |
|---|---:|---:|---:|---:|---|
| [C01 编辑与删除竞争](compact-20261110/jmeter/C01/assertions.json) | 2 × 20 | 40 | 20 | 20 | 9 轮编辑获胜，核对更新后的标语和版本。11 轮删除获胜，核对电影不存在。 |
| [C02 并发创建同一组合键](compact-20261110/jmeter/C02/assertions.json) | 10 × 20 | 200 | 20 | 180 | 每轮只保留一条与指定名称和导演 ID 匹配的电影。 |
| [C03 部分重叠导入](compact-20261110/jmeter/C03/assertions.json) | 2 × 20 | 40 | 20 | 20 | 20 次冲突均在 `movies[1].director`。每轮精确核对获胜文件的两部电影，以及两份文件对应的历史状态与计数。 |
| **合计** | | **280** | **60** | **220** | **非预期失败、JTL 失败、重复组合和失败导入残留均为 0** |

C03 新增 40 部电影、40 条坐标、20 人和 20 个地点，均来自获胜文件。场景目录包含 JTL、HTML 报告、请求响应记录和前后数据库快照。[JMeter 汇总](compact-20261110/jmeter/summary.json) · [C03 HTML](compact-20261110/jmeter/C03/html/index.html)

功能验收另行通过 17 项 HTTP 检查，覆盖登录、CSRF、文件入口约束、成功导入、失败历史和角色权限。一项追加检查上传了第一条合法、第二条 `length=0` 的文件。服务器返回 HTTP 400，四张领域表的行数和集合版本均无变化，历史保留失败状态，新增数量为空。[17 项 HTTP 检查](compact-20261110/functional/http-functional.json) · [末条字段检查](compact-20261110/functional/invalid-last-field.json)

重跑命令见 [JMeter 说明](../../movie-lab/jmeter/README.md)。完整验收证据在 [compact-20261110](compact-20261110/)。
