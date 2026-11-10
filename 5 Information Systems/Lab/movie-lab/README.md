# 实验二 · 电影管理系统

本项目在实验一的电影管理系统上增加了 JSON 批量导入、按角色查看导入历史，以及仅在业务层执行的“电影名称＋导演”唯一校验。以下步骤适用于已部署的 Helios 实验二。

## 1. 从 Windows 登录 Helios

在 **Windows PowerShell** 运行下列命令，按 SSH 的提示输入登录凭据。

```powershell
ssh -p 2222 s407960@helios.cs.ifmo.ru
```

登录后，在 **Helios 终端** 检查实验二目录和进程。SSH 登录默认进入家目录，项目的 `scripts/helios.py` 在 `is-lab2-4101` 目录内。

```sh
cd /home/studs/s407960/is-lab2-4101 && python3.11 scripts/helios.py status
```

若显示 `Running PID ...`，先检查 HTTP 是否就绪。若显示 `Not running`，检查启动所需文件。

```sh
ls -lh target/movie-lab.war .runtime/payara-micro-6.2025.1.jar
```

## 2. WAR 缺失时先重新打包

这次日志中，`helios.py test` 执行的 Maven `clean` 已删除 `target/`，随后 JUnit 因 `lab2_4101_test_coordinates` 已存在而退出。这一轮构建没有生成新的 WAR。正式表已存在，所以 `init` 返回 `lab2_4101_coordinates already exists`。已有正式部署的恢复路径是**打包 → 启动 → 验证 HTTP → 建隧道**。

如果 WAR 缺失或需要重新构建，先确认本项目的 Payara 进程已停止，再在 **Helios 项目目录** 执行下列命令。这里用 `-DskipTests` 将恢复运行与测试表问题分开。

```sh
cd /home/studs/s407960/is-lab2-4101 &&
env -u _JAVA_OPTIONS JAVA_HOME=/usr/local/openjdk21 PATH="/usr/local/openjdk21/bin:$PATH" \
  MAVEN_OPTS='-Xmx384m -XX:MaxMetaspaceSize=256m -XX:ActiveProcessorCount=2' \
  mvn -B -ntp -s scripts/maven-settings.xml -DskipTests package &&
test -s target/movie-lab.war && ls -lh target/movie-lab.war
```

确认 Maven 显示 `BUILD SUCCESS`，且列出了非空的 `target/movie-lab.war`。`-DskipTests package` 的结果是部署包，完整测试另见第 5 节。

## 3. 启动并确认服务器端 HTTP 就绪

在 **Helios 项目目录** 执行。两个文件检查通过后，才会启动 Payara。

```sh
test -s target/movie-lab.war &&
test -s .runtime/payara-micro-6.2025.1.jar &&
MOVIE_TARGET=production MOVIE_HTTP_PORT=40797 MOVIE_ISOLATION='READ COMMITTED' python3.11 scripts/helios.py start
```

`Started PID ...` 只说明启动脚本创建了 Java 子进程。Payara 完成部署后再检查首页和认证接口，两个请求都应返回 `200`。

```sh
python3.11 scripts/helios.py status
python3.11 -c 'from urllib.request import urlopen; base="http://127.0.0.1:40797/movie-lab/"; print("Page:", urlopen(base, timeout=8).status); print("Auth API:", urlopen(base+"api/auth", timeout=8).status)'
```

若启动期间暂时返回 `503`，等部署完成后再检查。若进程很快退出、反复启动得到不同 PID，或 HTTP 持续失败，查看日志末尾。

```sh
tail -n 80 .runtime/payara.log
```

| 现象 | 检查或处理 |
| --- | --- |
| `can't open file '/home/studs/s407960/scripts/helios.py'` | 当前位于家目录。先 `cd /home/studs/s407960/is-lab2-4101`。 |
| 日志提示 WAR 不存在 | 按第 2 节打包。测试的 `clean` 会先删除旧 `target/`。 |
| Payara JAR 不存在 | 检查 `.runtime/payara-micro-6.2025.1.jar`。启动脚本依赖 Maven 构件 `fish.payara.extras:payara-micro:6.2025.1` 的 JAR，需放在该路径。 |
| `This deployment is already running` | 用 `status` 和上面的 HTTP 检查验证现有进程。 |
| `Address already in use` | 用 `sockstat -4 -l -p 40797` 查看占用。确认进程归属后再处理。 |
| `.pgpass` 或数据库认证错误 | 检查 Helios 的 `~/.pgpass` 权限为 `0600`，存在匹配 `pg:5432:studs:s407960` 的条目。对外分享日志时隐去凭据。 |
| 正式表 `lab2_4101_coordinates already exists` | `init` 仅用于空库。已部署实例按第 3 节启动。 |

需要明确停止或重启时，在 Helios 项目目录单独执行 `python3.11 scripts/helios.py stop`，确认 `status` 显示 `Not running` 后再启动。

## 4. 从 Windows 打开网页

服务器端 HTTP 正常后，在**另一个 Windows PowerShell 窗口**建立 SSH 隧道。

```powershell
ssh -N -L 18083:127.0.0.1:40797 -o ExitOnForwardFailure=yes -p 2222 s407960@helios.cs.ifmo.ru
```

隧道连接后窗口通常会安静等待。保持窗口打开，再用浏览器访问 [http://127.0.0.1:18083/movie-lab/](http://127.0.0.1:18083/movie-lab/)。`40797` 是 Helios 上的服务端口，`18083` 是 Windows 上的隧道入口。若 Windows 的 `18083` 已被占用，可把命令和浏览器地址中的 `18083` 同时改成空闲端口。此窗口中的 `Ctrl+C` 会关闭隧道。

网页使用独立的应用账号，可通过俄语页面的 `Зарегистрироваться` 注册。需要授予管理员权限时，在 Helios 项目目录对已注册的用户执行 `MOVIE_ADMIN_USER=实际用户名 python3.11 scripts/helios.py admin`。

## 5. 初始化、迁移和测试是独立操作

| 命令 | 适用场景 |
| --- | --- |
| `python3.11 scripts/helios.py init` | 仅在首次部署、正式表尚未建立时创建正式表。 |
| `python3.11 scripts/helios.py migrate` | 需要将已有实验二表升级到当前结构时，应用 `database/migrations/` 中的迁移。 |
| `python3.11 scripts/helios.py test` | 可选的 PostgreSQL 集成测试。先停实验二应用并确认 `lab2_4101_test_` 测试表不存在。这条命令会清理 `target/`，测试失败后可按第 2 节恢复部署包。 |
| `python3.11 scripts/helios.py init-test`、`start-test` | 单独准备和启动 Web/JMeter 测试实例。测试实例与正式实例共用实验二启动脚本的 PID 文件和默认 HTTP 端口。 |

JUnit 会自己创建测试表。出现 `lab2_4101_test_coordinates already exists` 时，说明测试库已存在，可能是先前 Web/JMeter 留下的。可先用下列只读查询确认，保留已有数据，按 [JMeter 说明](jmeter/README.md) 决定是否需要备份和整理测试环境。要先恢复网页，直接按第 2、3 节操作。

```sh
psql -X -h pg -p 5432 -U s407960 -d studs -w -c \
  "SELECT tablename FROM pg_tables WHERE schemaname = 's407960' AND starts_with(tablename, 'lab2_4101_test_') ORDER BY tablename;"
```

Helios 使用 `pg:5432/studs`，schema 为 `s407960`。实验二正式表使用 `lab2_4101_` 前缀，集成测试和 JMeter 使用 `lab2_4101_test_`，实验一使用 `lab1_4101_`。JUnit 与 Web/JMeter 按顺序使用测试表。

## 6. 源码和交付位置

- `src/main/java/ru/itmo/movie/` 放 Java 后端，`src/main/webapp/` 放俄语网页。导入时整批数据在同一事务内写入，历史权限由后端校验。电影唯一键比较原样名称和导演 `Person.id`，两部同名且均无导演的电影也会冲突。
- [导入契约](docs/import-format-ru.md)和 [JSON 样例](src/main/webapp/examples/import-valid.json)可用于网页演示。
- [JMeter 运行说明](jmeter/README.md)覆盖三个验收场景。新结果和复现入口见 [验收索引](../verification/Lab2/ACCEPTANCE.md)和 [Helios 部署记录](../verification/Lab2/DEPLOYMENT.md)。
- [俄语实验报告](../report/Lab2/report.pdf)及 LaTeX 源码在 `../report/Lab2/`，UML 图在 `../report/Lab2/uml/`。
- 本地开发可在 Windows 项目目录执行 `./scripts/start-local.ps1`，使用独立的本地数据库，默认网页端口为 `18081`。连接 Helios 时使用第 4 节的 `18083` 隧道入口。

