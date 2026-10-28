# 隔离级别实测与最终选择

执行日期：2026-10-28（Europe/Moscow）。环境：Helios FreeBSD14.5、PostgreSQL18.3、Payara6.2025.1。最终保留 **READ COMMITTED + AppState 全局写锁 + 客户端版本 / @Version**。没有为凑结论提高所有事务的隔离级别。

## 真实配置与控制变量

- 同一最终 WAR：`cf386061ed67f25abac1f84cf13b61fdcb4a988dddbfe3363c81e670365d0576`。
- 同一私有测试数据快照 SHA256：`1de7624b8a85df0c46a58bc063a22814231e64e4168862642b543231afe9cbd5`。快照含测试账号，只留在服务器 .runtime，不纳入交付。
- 两组均由 scripts/lab2-compare.py 恢复同一快照；相同锁、线程、20轮、重试上限3、HTTP目标127.0.0.1:40797。2线程用于双人竞争，其他场景10线程；C02D单列双删除。
- Java业务类与140项服务器测试时一致，见 server/final/tested-classes-and-war.json。JUnit实际EclipseLink4.0.5，Web实际4.0.1.payara-p3；服务器JMeter覆盖了真实容器版本。
- Database.write 在事务首次业务查询前执行 SET TRANSACTION ISOLATION LEVEL，然后 SET LOCAL lock_timeout，再获取 AppState行锁，最后读版本、查重和写入。JUnit在这一实际业务连接里SHOW出read committed；metadata连接也实测read committed。SERIALIZABLE组执行同一路径的显式SET，真实40001与重试日志证明该级别被使用。
- 首轮新增功能的当前策略 controlled-RC-A 亦通过1640请求；较早的原始Lab1基线因缺失测试PU失败，未声称原始基线全绿。final-RC在最终俄语说明资源打包后再次全部通过。

## 同一最终 WAR 的结果

| 场景 | RC目标请求 | RC预期冲突 | RC平均/P95 ms | SERIALIZABLE实际请求/计划 | SERIALIZABLE平均/P95 ms | 对照结果 |
|---|---:|---:|---:|---:|---:|---|
| C01 | 40 | 20 | 140.10/2049 | 40/40 | 154.95/2072 | 通过 |
| C02 | 40 | 20 | 142.50/2072 | 40/40 | 47.38/129 | 通过 |
| C02D | 40 | 20 | 120.70/2030 | 40/40 | 134.18/2033 | 通过 |
| C03 | 200 | 180 | 189.03/3165 | 200/200 | 248.02/272 | 通过 |
| C04 | 200 | 180 | 191.32/103 | 200/200 | 441.19/2237 | 通过 |
| C05 | 200 | 0 | 220.72/2097 | 10/200 | 3226.30/3312 | 未通过；余下轮次未执行 |
| C06 | 40 | 20 | 38.50/128 | 40/40 | 41.80/74 | 通过 |
| C07 | 200 | 180 | 234.60/3048 | 200/200 | 749.75/3205 | 通过 |
| C08 | 40 | 20 | 33.08/55 | 40/40 | 43.25/78 | 通过 |
| C09 | 40 | 20 | 39.73/66 | 40/40 | 164.07/2081 | 通过 |
| C10 | 200 | 20 | 346.15/3097 | 10/200 | 192.50/266 | 未通过；余下轮次未执行 |
| C11 | 200 | 0 | 6.92/29 | 200/200 | 22.09/32 | 通过 |
| C12 | 200 | 0 | 169.19/334 | 10/200 | 249.20/308 | 未通过；余下轮次未执行 |

RC：1640目标请求 = 780次写入提交 + 680次预期409/404 + 180次读取；非预期失败0，序列化重试0，全部13个变体各20轮完成。

SERIALIZABLE：实际1070目标请求，225次写入提交、661次预期冲突、180次读取和4次非预期失败；517次序列化重试。C05、C10、C12各只完成首轮，因503而触发JMeter停止，后19轮没有执行，不能计入通过。JMeter本身退出0也未被当成通过：JTL失败和Python断言使总runner返回1。

两组实际数据库重复组合均为0，失败导入辅助对象残留为0。SERIALIZABLE的拒绝保持原子性，但在固定3次重试限制下损害了合法写入的完成率；不能把这些503归类为允许的业务409。第一次较早版本对照也出现3次非预期失败和527次重试，原始日志同样保留。

## 最终决策及原因

| 事务 | 修改前/当前策略的实测 | 最终配置 | 理由与证据 |
|---|---|---|---|
| CRUD/特殊操作 | READ COMMITTED，AppState FOR UPDATE；140项服务器测试含版本、约束和特殊操作 | 显式READ COMMITTED，同一写锁，保留客户端版本和@Version | final-RC/C01–C06、C10、C12；准确赢家、版本和最终状态 |
| 整批导入 | 单个RESOURCE_LOCAL业务事务；锁后解析关联/查重；flush不提交 | 显式READ COMMITTED；同一事务内SUCCESS+所有领域对象+一次revision | final-RC/C07–C11；JUnit F08/F09/C11在真实flush后及commit失败时证明全批回滚 |
| 历史短事务 | 独立EntityManager，READ COMMITTED，无movie revision | 保留READ COMMITTED | T1保存RUNNING，T3保存FAILED；成功终态仍在T2；server/production/history-poll.json证明失败历史变化时revision8→8 |

PostgreSQL READ COMMITTED的每条语句使用已提交视图；后到的写事务取得同一AppState锁后，能在最终查询中看见前一提交。全局锁保护尚不存在的电影组合，版本检查保护用户旧表单；单独@Version不能防止两个新对象同时不存在的竞态。SERIALIZABLE的快照可能在竞争AppState行时过期，40001后必须用新EntityManager重跑整个事务。本实现仅重试已经确认回滚的40001，不重试业务错误、旧版本或未知commit。参见[PostgreSQL官方隔离说明](https://www.postgresql.org/docs/18/transaction-iso.html)。

实测锁等待：JUnit设置200ms，首轮观察217ms/55P03；部署Web默认10000ms探针观察10.038秒后503 DATABASE_TEMPORARY，见 server/final/http-lock-timeout.json。JPA hint本身没有被当成有效超时证据。

## 局限和未执行项

- 共享Helios存在调度和JIT噪声；失败场景提前停止，不能拿聚合平均数声称公平的吞吐提升。可对比首个失败前完整执行的C03/C04，但这些时延也只是此环境的观察。
- 全局写锁会让长导入阻塞其他写入；默认5MiB/1000条是工程上限，本次并发文件为2条，未执行1000条满额导入的性能压测。
- 未主动制造网络在commit响应瞬间断开导致结果未知的端到端故障。代码会先查新连接中的历史，已SUCCESS不覆盖，无法核实时保留RUNNING；不得将此未注入分支写成已实测通过。F09实测的是明确的延迟约束commit回滚。
- 部署与RUNNING恢复针对单实例；未宣称已验证多实例归属/存活协议。实际恢复测试通过显式SQL创建孤立RUNNING，再停止旧进程并重启，属于可复现恢复夹具，不是伪称发生了真实网络不确定提交。

## 复现

在服务器已准备私有基线后：`python3.11 scripts/lab2-compare.py <new-RC-id> "READ COMMITTED"`；随后`python3.11 scripts/lab2-compare.py <new-SER-id> SERIALIZABLE`。每次先停止自己的候选实例、恢复限定的测试表，再启动相同WAR；不要在正式表上运行恢复脚本。完成对照后正式服务使用`MOVIE_ISOLATION="READ COMMITTED" python3.11 scripts/helios.py start`。

原始配置和证据：server/final-RC/、server/final-SERIALIZABLE/ 中的 configuration.json、run-statistics.json、C*/responses.jsonl、JTL、HTML、assertions.json及数据库前后快照。JMeter按[官方CLI说明](https://jmeter.apache.org/usermanual/get-started.html#load_test_running)在Helios本机运行，未用本地结果替代。