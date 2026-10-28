# 实验二实际验收索引

日期：2026-10-28，Europe/Moscow。**实验二功能、服务器构建/测试、最终并发配置与正式部署已完成。** 本表只把真实执行项计入通过；隔离研究中的失败对照和未注入故障另列。

- Helios：`s407960@helios.cs.ifmo.ru:2222`，`/home/studs/s407960/is-lab2-4101`；正式表 `s407960.lab2_4101_*`，测试表 `lab2_4101_test_*`。
- 全套测试所用 WAR：`cf386061ed67f25abac1f84cf13b61fdcb4a988dddbfe3363c81e670365d0576`；原始服务器与下载件相同。
- 当前 UI 修订 WAR：`867545d9dbbf8d18e9d224e3b29b0c7387ab49458b9f8ed44d7421cbec3f87f4`；服务器 Maven package 及浏览器复核通过。只有四个前端条目变化，其余全部 WAR 条目字节一致；本次没有重跑140项测试及JMeter。见 `ui-review/` 与 `browser/final-ui-checks.json`。
- Java clean verify：140 tests，0 failures/errors/skips。静态俄语说明重新打包后，所有 Java class 哈希与该测试版本相同。
- 最终 RC JMeter：13 个变体（C02D 单列），每个 20 轮；1640 目标请求，780 写入提交，680 预期冲突，180 读取，非预期失败 0。
- 同一 WAR、同一快照的 SERIALIZABLE 对照未通过：517 次重试、4 次非预期失败，C05/C10/C12 的后续轮次未执行，不计通过。最终采用显式 READ COMMITTED＋AppState 写锁＋版本检查。
- 原始服务器证据归档已下载；10868 个文件逐项 SHA-256 匹配。续作恢复和补测位于 `resume/`，不改写原始归档。

## 需求到交付

| 需求 | 实际结果 | 交付 / 证据 |
|---|---|---|
| R1 Web JSON 上传 | 通过，真实文件选择器、multipart 和原始 File | `browser/final-import-success.png`；`server/production/http-functional.json`；ImportResource/ImportParser |
| R2 整批原子性 | 通过，末条错误、首条 flush 后异常和 commit 延迟错误均无领域残留 | JUnit F03/F08/F09/C11；`resume/last-row-check.json`；`server/final-RC/C07`–`C11` |
| R3 原领域约束及嵌套对象 | 通过，严格类型/字段/数值矩阵及人物复用 | 140 项服务/解析器/数据库测试；`movie-lab/src/test/resources/import/` |
| R4 角色历史范围 | 通过，服务器过滤 items/total/详情；普通注册禁止 role | HTTP H01–H05；`browser/final-history-user.png`、`final-history-admin.png` |
| R5 历史字段与成功数量 | 通过，失败数量为空，成功和业务同提交，独立失败历史 | HTTP、JUnit H06、`server/production/history-poll.json`、`restart-result.json` |
| R6 名称＋导演业务唯一 | 通过，无新数据库唯一索引/触发器 | JUnit U01–U08；`server/production/database-audit.json`；`server/final-RC/C03`–`C09` |
| R7 JMeter 并发 | 通过最终 RC 配置；所有 C 场景及双删除变体 | `movie-lab/jmeter/`；`server/final-RC/summary.json` 及每组 JTL/HTML/断言/快照 |
| R8 隔离性研究 | 完成，保留 RC 的决定有同 WAR/快照对照 | `isolation-analysis.md`；`server/final-SERIALIZABLE/`；两组 configuration.json |
| R9 报告与 UML | 已提供俄语 TeX/PDF、DOT 和 PNG/SVG/PDF 图 | `report/Lab2/`；`report-final-compile.log`；`report-final-render/` |
| R10 Helios 实测部署 | 通过 S01–S06；本地未作为服务器结果替代 | 下表；`DEPLOYMENT.md`；`download-integrity.json` |

表中源码/报告路径相对于 `Lab/`；其他证据路径相对于本目录。

## F：功能与字段

共同服务器测试证据：[最终构建日志](server/final/build-test.log)、[Surefire 明细](server/final/surefire-reports/)、[JUnit 源码](../../movie-lab/src/test/java/ru/itmo/movie/MovieServiceTest.java)。字段矩阵通过动态用例展开；不把仅存在的 fixture 当成已运行结果。

| ID | 实际结果与范围 | 证据 |
|---|---|---|
| F01 | 通过；Web 双记录上传成功，新增 2 Movie，按护照共用 Person，数量 2 | JUnit `F01_F07_exactIntegersPersonReuseAndSingleRevision`；正式 HTTP 17 项；`browser/final-import-success.png` |
| F02 | 通过；Movie/Coordinates/Person/Location 必需字段省略/null、非法枚举/类型矩阵均拒绝并返回路径 | JUnit `F02_F04_F06_strictFieldMatrix`；严格解析源码 |
| F03 | 通过；末条 length=0 整批拒绝、四类表及 revision 不变；末条重复在真实写入后整批回滚 | `resume/last-row-check.json`（操作 9，独立runId）；JUnit `F03_U06_lastDuplicateRollsBackAllNestedObjects` |
| F04 | 通过所列字段矩阵：x=826/827、整型范围、正数零/负值/1、nullable、浮点溢出/下溢 | JUnit 字段矩阵、`F04_F05_F06_validBoundaries` 及原 Lab1 字段/SQL 约束测试 |
| F05 | 通过；USA≤total，等值、null 总票房及不合法关系分别断言 | 原服务/数据库 BoxOffice 测试；解析器边界测试 |
| F06 | 通过；Long 最大值、越界及 2^53+1 精确保留，整数小数/越界、浮点非有限/下溢、无时区生日拒绝 | JUnit 严格矩阵及精确预算持久化断言 |
| F07 | 通过；跨记录/角色复用、已有一致人物复用、冲突不覆盖、等价秒格式及不同时区身份 | JUnit 两个 F07 测试与精确整数/人物计数测试 |
| F08 | 通过；saveImported 真正 INSERT/flush 并取得 ID 后抛异常，四类表无净增加，FAILED 保留 | JUnit `F08_failureAfterActualInsertFlush` |
| F09 | 通过明确的 commit 回滚；测试专用 deferred constraint trigger 在 commit 抛错，业务全回滚，FAILED 保留；触发器随后删除 | JUnit `F09_actualDeferredCommitFailure`；同批 U08 审计 |
| F10 | 通过；空数组、坏 JSON、未知/重复/生成字段、坏编码、BOM、错误媒体类型、空/缺文件、超限；入口拒绝不留历史，接受后解析失败留 FAILED | JUnit F10；`server/production/http-functional.json`；同名 candidate 结果 |

F09 的网络中断导致 commit 结果未知分支**未做端到端注入**，不能与已实测的明确回滚混同。

## U / H：唯一性与权限

| ID | 实际结果 | 证据 |
|---|---|---|
| U01 | 同名＋同 Person 再建返回 DUPLICATE_MOVIE；仅一条 | JUnit U 综合测试；final-RC/C03 |
| U02 | 同名不同 Person、不同名同导演、导演同名不同身份可并存 | JUnit U 综合测试；final-RC/C05 |
| U03 | 两次同名 null 导演冲突，有导演与无导演可并存 | JUnit U 综合测试；final-RC/C04 |
| U04 | 自身组合允许；与他人组合冲突且失败者原记录保留 | JUnit；final-RC/C06 的原记录/目标键断言 |
| U05 | 部分更新按合并后的组合检查，含导演改为空的冲突 | JUnit U 综合测试；saveInTransaction 共用校验 |
| U06 | 文件内部、与数据库及重复整份文件均整批拒绝 | JUnit F03/U06；正式 HTTP duplicate；final-RC/C07–C09 |
| U07 | 大小写/首尾空格/分隔符精确比较，人物姓名和护照修改不改变 ID | JUnit `U01_U02_U03_U04_U05_U07_identityNullPartialAndExactNames` |
| U08 | pg_constraint/pg_index/pg_trigger 确认 Movie 无组合唯一或自定义触发器；旧 passport/username 唯一保留 | JUnit U08；`server/production/database-audit.json`；schema/ORM/迁移源码 |
| H01 | A/B 各自仅见本人；SUCCESS 有实际数量，FAILED 为 null/界面“—” | HTTP、JUnit H 综合；最终用户截图 |
| H02 | 两名管理员均可查全体、分页 total 一致 | HTTP、JUnit；最终管理员截图 |
| H03 | 猜他人 ID 返回404、userId 参数不越权、注册 role=ADMIN 拒绝 | HTTP17项、JUnit详情权限断言 |
| H04 | 真实进程重启后账号/角色/终态历史/电影保存；续作恢复再次核对 | `server/production/restart-result.json`；`resume/runtime.json`、`snapshot.json` |
| H05 | 401、403、独立 Session/CSRF 和并发身份正确 | HTTP17项、JMeter Cookie Manager、双浏览器主机 Cookie 上下文 |
| H06 | flush 暂停时 RUNNING 且数量空；成功/回滚后终态正确；失败历史能独立轮询 | JUnit C11/H06；`server/production/history-poll.json`（revision8→8）；浏览器检查 JSON |

## C：最终 READ COMMITTED 实测

每行证据为 `server/final-RC/<ID>/`，包含 fixture、原始 responses.jsonl、JTL、HTML、assertions.json、数据库前后快照；总索引 [summary.json](server/final-RC/summary.json)。

| ID | 线程×轮次 | 实际结果 |
|---|---:|---|
| C01 | 2×20 | 每轮恰好一个更新胜者、一个409；初始版本+1、最终值属于胜者 |
| C02 | 2×20 | update/delete 恰好一个成功；删除胜时对象不存在，更新胜时保留更新，失败码精确核验 |
| C02D | 2×20 | 双删除恰好一次成功，另一次404 |
| C03 | 10×20 | 共20次201、180次DUPLICATE_MOVIE；每个共享导演组合一条 |
| C04 | 10×20 | null导演分支同样20次201、180次冲突 |
| C05 | 10×20 | 200次合法创建全部成功，无错误单字段唯一性 |
| C06 | 2×20 | 每轮仅一条修改到目标键；失败者原行保留，无误删 |
| C07 | 10×20 | 每轮一整份文件成功，其他409；领域辅助对象只来自成功批次，全部接受请求有历史 |
| C08 | 2×20 | CRUD和导入仅一个路径提交共享键；失败导入的独有记录也回滚 |
| C09 | 2×20 | 仅一整批提交，共同键和独有键符合胜者，另一文件无部分提交 |
| C10 | 10×20 | 每轮失败导入409，独立CRUD均按精确预期提交，失败导入无领域残留 |
| C11 | 10×20 | 读只见0或2；成功后全部可见；另由真实数据库 latch 测试确定性覆盖 flush 前后及回滚 |
| C12 | 10×20 | 混合CRUD/导入/真实award全部通过，最终奖数精确，无丢失更新/重复/孤立引用 |

SERIALIZABLE 不是最终通过配置。其 C05/C10/C12 只运行首轮、共4次非预期失败；其他未执行轮次在 [隔离研究](isolation-analysis.md) 中明确标记。

## S01–S06：服务器要求

| ID | 结果 | 证据 |
|---|---|---|
| S01 | 已认证、核实服务器/数据库/端口和隔离边界；quota命令不可用已记录 | `helios-environment.md`、原始环境与基线日志 |
| S02 | 隔离目录、完整PU/前缀映射、原数据复制迁移两次、源码清单与WAR哈希 | `server/candidate/migration.json`、source-manifest、`server/final/tested-classes-and-war.json` |
| S03 | Helios Maven clean verify实际执行140项全部通过，无跳过；保留原基线失败 | `server/final/build-test.log`、Surefire；`server/baseline/` |
| S04 | 真实远程候选及正式应用、两用户两管理员、隧道浏览器上传/权限/同步/旧表单 | `browser/final-checks.json` 及截图；正式HTTP JSON |
| S05 | JMeter在Helios本机CLI运行全部C场景并比较隔离级别，解析JTL及核对数据库 | final-RC / final-SERIALIZABLE 原始目录、配置和统计 |
| S06 | 相同WAR正式部署、真实进程重启、Lab1指纹不变、证据下载逐文件哈希校验；续作恢复同WAR | production/deployment/restart/audit JSON；`download-integrity.json`；`resume/`；`DEPLOYMENT.md` |

## 边界与未执行项

1. 未注入“网络恰在commit确认时断开”的端到端故障；实现有新连接核实/保留RUNNING分支，不伪称已实测。
2. 未做1000条满额文件的吞吐压测；并发文件为两条，工程限额不等于性能承诺。
3. 单实例部署与恢复；未宣称验证多实例操作归属协议。
4. 05:00曾观察到进程退出，应用日志不足以确定原因。续作时已恢复并核对数据；不宣称服务器会永久保持进程运行。
5. 较早失败、试跑和中文界面截图均为历史开发证据，不能替代最终目录。最终俄语界面及顶部编号删除按用户后续指令执行。
