# 实验二：Helios 部署与服务器测试计划

本文件补充 [主执行计划](lab2_execution_plan.md) 与 [验收计划](lab2_acceptance_plan.md)。用户于 2026-10-28 明确要求实验在服务器上运行测试，并提供了 SSH 账号和密码。这里记录执行方案；本次仅补充文档和本机凭据，尚未登录服务器或开展测试。

## 1. 连接信息与凭据

| 项目 | 值/状态 |
|---|---|
| SSH 主机 | `helios.cs.ifmo.ru` |
| SSH 端口 | `2222` |
| SSH 用户 | `s407960` |
| SSH 密码 | 用户已提供，保存于下述仓库外加密文件 |
| 历史实验一目录 | `/home/studs/s407960/is-lab1-4101`，来自现有代码/README，执行时核实 |
| 历史数据库地址 | `pg:5432/studs`，账号与 schema 为 `s407960`，执行时核实 |
| 历史应用监听 | `127.0.0.1:40796`，不能据此假定端口当前空闲 |

直接连接命令（密码在 SSH 提示时输入，不属于命令参数）：

```powershell
ssh s407960@helios.cs.ifmo.ru -p 2222
```

本机凭据位置：

```text
C:\Users\CHL\AppData\Local\MovieLab\credentials\helios-s407960-lab2.clixml
```

凭据已保存为 Windows 当前用户加密的 PSCredential，并完成保存/读取一致性检查；这仅验证本机凭据可读取，不代表服务器认证已经验证。同一电脑、同一 Windows 用户下的执行 AI 可读取：

```powershell
$heliosCredential = Import-Clixml -LiteralPath 'C:\Users\CHL\AppData\Local\MovieLab\credentials\helios-s407960-lab2.clixml'
```

读取后仅向 SSH 认证接口提供用户名/密码，明文只在认证所需的进程内存中使用；不要输出整个凭据、解密后的密码或将密码拼入命令行。SSH 库/交互工具应沿用已验证的 known_hosts，不通过关闭主机校验绕过身份检查。

加密文件不在仓库中，不加入源码包、报告或测试结果。跨电脑/Windows 用户移交时不能直接解密，应通过执行环境的凭据渠道重新提供 SSH 密码。服务器数据库密码优先沿用脚本读取的 `~/.pgpass`，核实权限与匹配条目即可，不打印内容；缺失时再用用户提供的登录凭据按实验一数据库约定配置并验证。

## 2. 必须隔离的服务器资源

推荐默认值如下，均是拟采用的部署设计，尚未在服务器确认。先检查目录、端口及表的归属；存在占用时选择新的专用资源并记录实际值。

| 资源 | 实验二建议值 |
|---|---|
| 项目目录 | `/home/studs/s407960/is-lab2-4101`，根目录直接包含 pom.xml、src、scripts、jmeter |
| 服务器 HTTP | `127.0.0.1:40797`，空闲时使用 |
| 本地隧道端口 | `18083`，空闲时使用 |
| 正式实验二数据表 | schema `s407960` 下 `lab2_4101_` 前缀 |
| 集成/端到端测试表 | 同一 schema 下 `lab2_4101_test_` 前缀；两类测试顺序执行，避免互相清理 |
| 服务器证据目录 | 项目内 `verification/Lab2/<runId>/` |
| 本地证据目录 | `Lab/verification/Lab2/<runId>/` |

保留原实验一目录、进程和 `lab1_4101_` 表。实验二新目录使用现有项目的改进版本；如需验证旧数据迁移，使用实验一数据的独立副本，不直接清理原表。共享 schema 中的清理精确限定实验二测试表，不运行 DROP SCHEMA CASCADE。

## 3. 执行顺序与完成标准

### S01：服务器环境核查

1. 使用上述账号连接，记录 hostname、当前用户、实际工作目录、Java/Maven/Python/PostgreSQL 客户端版本、JMeter 可用性及磁盘配额。
2. 检查本人现有进程和监听端口，核实实验一位置、数据库可连接性、表前缀、schema 权限。服务器可能不是 Linux，运行命令前先确认系统，避免依赖不存在的 systemd/apt。
3. 将实际环境写入 `verification/Lab2/helios-environment.md`，密码/Token 不进入记录。

完成条件：能够认证并连接实际数据库，项目和测试资源的隔离边界明确；记录使用的端口和工具路径。

### S02：准备可在 Helios 执行的代码与映射

当前 `scripts/helios.py` 可作为改造基础，**不能直接当作已适配实验二的脚本**：

- Java 路径、Payara JAR、HTTP 40796 和 `lab1_4101_` 前缀目前写死；改成实验二实际配置或明确的参数。
- 当前 `test` 模式设置 `MOVIE_TEST_SCHEMA=s407960`；测试 SQL 的表名替换和清理同样写死实验一测试前缀，需要统一修改。
- 补全 `movies-helios-test` 持久化单元及 `orm-helios-test.xml`；正式 `movies-helios` 映射到实验二正式表，测试单元映射到实验二测试表，所有新实体均列入映射。
- DDL 替换规则目前仅枚举旧实体，需覆盖 ImportOperation 表、外键、索引和新增迁移。避免出现有前缀的主表引用无前缀历史表等问题。
- 测试清理加入新增历史表并遵守外键顺序；不能让测试结束时删除正式表。
- 运行时目录、PID 文件、日志、端口与原实验一分离；停止操作验证 PID 对应本部署，只停止自己的实例。

准备源码包，包含 pom.xml、src、database、scripts、jmeter、必要文档；排除本地 .runtime、凭据、数据库目录、过期 target 与缓存。记录包哈希，经 SCP/SFTP 上传到已确认的实验二目录；在服务器构建后记录 WAR 哈希。

完成条件：新旧库迁移路径及所有实体映射核对通过，测试数据库目标精确可辨；远程包与本地准备的源码一致。

### S03：在服务器构建与集成测试

在完成 S02 改造后的远程项目根目录执行。以下命令沿用现有脚本入口；实际 Python 路径以 S01 为准：

```sh
python3.11 scripts/helios.py test
```

脚本应在服务器运行 Maven clean verify，连接 `pg:5432/studs` 的隔离测试表，覆盖原测试和实验二新增 F/U/H 用例中适合服务/数据库层的部分。先测试全新 schema DDL，再用独立旧结构副本测试增量迁移；正常迁移不丢数据。

保存标准输出/错误、进程退出码、Surefire 报告和测试用例数量。连接失败、映射缺失、跳过用例或仅编译成功均不能算服务器测试通过。

完成条件：服务器构建成功，测试实际执行且全部通过，证据标明 Helios 环境和本次代码/WAR。

### S04：部署候选应用与 Web 验证

1. JUnit 清理结束后，为 Web/JMeter 初始化独立测试表；测试应用使用 `movies-helios-test`、专用运行时目录和选定 HTTP 端口。部署脚本必须支持这一模式，不让 JUnit 与 Web 测试同时操作同一组表。
2. 准备两名普通用户与两名管理员，服务器本机检查登录/健康响应。这里的 Web 账号与 SSH 账号是不同用途，不能复用 SSH 密码作公开演示凭据。
3. 本地建立隧道后，用浏览器完成 F/H 界面、认证、上传与双会话同步检查，确认请求目标就是服务器版本。

端口采用建议值时的隧道命令：

```powershell
ssh -N -L 18083:127.0.0.1:40797 -o ExitOnForwardFailure=yes -p 2222 s407960@helios.cs.ifmo.ru
```

通过隧道访问 `http://127.0.0.1:18083/movie-lab/`。若更换服务器端口或本地端口，同时更新命令、测试参数和最终说明。

完成条件：服务器候选应用实际可用，浏览器检查有对应截图/结果；本地静态页面或本地数据库上的结果不计入此项。

### S05：服务器内运行 JMeter 和隔离级别比较

1. 在 Helios 安装/使用用户目录下的 JMeter，记录版本和 Java 兼容性，使用 CLI；从小规模并发开始，沿用验收计划参数，避免将共享服务器压满。
2. JMeter HTTP 目标为服务器 `127.0.0.1:<实际端口>/movie-lab/api`，同一服务器执行全部 C 场景及隔离级别对照；不能只在本地运行 JMeter 后将结果复制过去。
3. 服务器运行 fixture 生成器和结果核验脚本，检查实际数据库状态、历史记录及成功/冲突计数；服务器本机 URL 不经过 SSH 隧道，从而减少隧道对计时的影响。

命令模板（在远程项目根目录执行；替换 runId、JMeter 路径和实际端口，先创建结果父目录）：

```sh
jmeter -n -t jmeter/lab2-concurrency.jmx -Jhost=127.0.0.1 -Jport=40797 -JbasePath=/movie-lab/api -Jscenario=C03 -Jthreads=10 -Jrounds=20 -l verification/Lab2/<runId>/results.jtl -j verification/Lab2/<runId>/jmeter.log -e -o verification/Lab2/<runId>/html
```

这条命令只示范 C03；执行脚本必须覆盖验收计划全部 C 场景，不能把单场景通过当作整体验收。若 Helios 有软件/资源限制导致无法运行，记录具体错误并继续修复；未经用户变更要求，不以本地替代结果宣布此项完成。

完成条件：服务器内实际产生 JTL、HTML、业务断言和数据库核验结果；隔离级别比较基于服务器实测，最终配置通过相同场景复核。

### S06：正式部署、结果下载与最终核对

1. 保存全部测试证据后，停止本次候选实例；将同一已验证 WAR 部署到实验二正式数据表/运行时配置。只迁移实验二目标表；先确认有无旧数据及必要备份。
2. 核对正式部署 WAR 与已测试产物哈希相同、隔离/锁/认证配置一致，执行非破坏性的登录、历史权限与功能冒烟测试；正式数据与压测夹具分离。重启后验证账号、角色和历史持久化。
3. 使用 SCP/SFTP 下载服务器证据到本地 `verification/Lab2/<runId>/`，包含构建/Surefire、JTL/HTML、数据库核验、服务器日志摘要、环境说明和部署哈希。
4. 下载后核对结果完整性，将服务器目录、PID/端口、数据库 schema/前缀、停止/重启方式、隧道命令和实际访问地址写入交接说明。

下载命令模板（本地执行，目标父目录预先创建）：

```powershell
scp -P 2222 -r s407960@helios.cs.ifmo.ru:/home/studs/s407960/is-lab2-4101/verification/Lab2/<runId> '<本地 Lab 绝对路径>/verification/Lab2/'
```

完成条件：S01–S06 全部有实际证据，服务器正式部署可访问，本地副本可审阅。`ACCEPTANCE.md` 同时列出 F/U/H/C 结果与 S01–S06；服务器未执行项不能标为通过。
