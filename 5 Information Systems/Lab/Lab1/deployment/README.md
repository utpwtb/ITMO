# Helios 部署与复测

远程目录：`/home/studs/s407960/is-lab1-4101`。本地源码：`../movie-lab/`。

## 打开应用

需要两个终端窗口：一个用于登录服务器并启动应用，另一个用于 SSH 转发。

先在第一个窗口登录服务器：

```sh
ssh -p 2222 s407960@helios.cs.ifmo.ru
cd ~/is-lab1-4101
python3.11 scripts/helios.py status
```

如果显示 `Not running`，执行：

```sh
python3.11 scripts/helios.py start
```

启动后等待约 30 秒，再确认网页服务已就绪：

```sh
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:40796/movie-lab/
```

输出 `200` 表示网页可以访问。仅有 `Running PID ...` 表示进程存在，应用可能还在启动。如果没有 `200`，查看日志：`tail -n 80 .runtime/payara.log`。

随后在自己电脑的**第二个终端窗口**执行，按提示输入学校 SSH 密码，并保持窗口打开：

```sh
ssh -N -L 18082:127.0.0.1:40796 -p 2222 -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 s407960@helios.cs.ifmo.ru
```

输入密码后没有新提示符、光标一直等待是正常现象。`-N` 表示只建立转发通道，不打开远程命令行；这个窗口无需继续输入命令。服务器管理命令应在第一个窗口执行。

如果转发窗口出现 `channel ... open failed: connect failed: Connection refused`，说明浏览器请求已经通过 SSH 到达服务器，但服务器的 `40796` 端口尚未接收连接。回到第一个窗口，确认应用已启动，并用上面的 `curl` 命令确认输出 `200`；随后刷新浏览器。转发窗口中先前打印的错误不会自动消失。若刷新时仍新增相同错误，可按 Ctrl+C 结束转发，再重新执行转发命令。

然后打开 <http://localhost:18082/movie-lab/>。可点击“Зарегистрироваться”创建自己的实验账号，也可使用 `student / student`；它与学校 SSH、数据库账号互相独立。注册账号保存在数据库中，服务重启后需要重新登录，但账号仍然存在。要测试多客户端同步，可以同时打开普通窗口和无痕窗口。

HTTP 仅监听服务器 `127.0.0.1:40796`，通过 SSH 隧道访问。若提示本地 18082 被占用，改命令左侧端口，例如 `18083:127.0.0.1:40796`，浏览器也改用 18083。不要同时启动两个占用相同本地端口的隧道。

## 登录服务器与服务管理

2026-10-02 已部署持久化注册功能，通过 38 项 PostgreSQL 集成测试和 32 项浏览器/API 检查（含重启后登录）。[本次记录](verification/auth-2026-10-02/README.md)。后续向现有安装上传新版源码后，先运行 `python3.11 scripts/helios.py test`，成功后执行 `python3.11 scripts/helios.py migrate` 增加账号表，再按下面的停止和启动方式发布 WAR。不要对已有数据再次执行 `init`。

```sh
ssh -p 2222 s407960@helios.cs.ifmo.ru
cd ~/is-lab1-4101
python3.11 scripts/helios.py status
```

启动应用：

```sh
python3.11 scripts/helios.py start
```

查看日志：

```sh
tail -n 80 .runtime/payara.log
```

需要停止应用时才执行：

```sh
python3.11 scripts/helios.py stop
```

`start` 在后台运行，退出 SSH 后仍可运行。启动是异步的，需等待日志出现部署完成，并检查网页。这里没有安装开机自启动；服务器重启或管理员结束进程后，需要重新启动。停止后应先用 `status` 确认进程已退出，再启动。

## 实际数据库配置

数据库主机 `pg`，端口 `5432`，数据库 `studs`，账号与 schema 均为 `s407960`。脚本从服务器已有的 `~/.pgpass` 读取数据库凭据，并通过进程环境传给 JDBC，不把密码写入源码、命令行参数或测试报告。

该账号不能创建新的 schema，因此部署使用 `s407960` 内的五张专用表：

| Java 实体 | 部署表 |
|---|---|
| Movie | lab1_4101_movie |
| Coordinates | lab1_4101_coordinates |
| Person | lab1_4101_person |
| Location | lab1_4101_location |
| AppState | lab1_4101_app_state |

`movies-helios` persistence unit 通过 ORM XML 覆盖表名，其他实体字段、校验及业务规则保持一致。本地仍默认使用 `movies` unit 和原表名。

首次初始化命令如下，**已经初始化的部署不要重复执行**：

```sh
python3.11 scripts/helios.py init
```

初始化在一个数据库事务中执行普通 `CREATE TABLE`，若已有同名部署表会失败并回滚，不会覆盖已有数据。

## 在 Helios 重新运行集成测试

```sh
cd ~/is-lab1-4101
python3.11 scripts/helios.py test
```

该命令执行 Maven `clean verify`，从当前源码构建 WAR，并直接连接学院 PostgreSQL。测试使用 `movies-helios-test` unit 和 `lab1_4101_test_` 前缀；只清理本次成功创建的测试表，不清空部署数据。不要同时启动两次测试。如发现遗留测试表，脚本会拒绝覆盖，需先确认上一次测试进程是否仍在运行。

测试证据位于远程 `target/surefire-reports/`；WAR 位于 `target/movie-lab.war`。测试成功后的 WAR 更新不会自动替换正在运行的应用，需要先停止服务、确认退出、再启动。

服务器使用 Java 21，Payara Micro 6.2025.1，Maven 3.8.4，学院 PostgreSQL 18.3。构建 JVM 和测试 JVM 均显式限制堆内存，避免 FreeBSD 按整机内存计算默认堆导致启动失败。

## 本机浏览器复测

需要 Node.js、Playwright 和 Chrome，并提前建立上述 SSH 隧道。在 `movie-lab` 目录使用 PowerShell：

```powershell
$env:MOVIE_BASE_URL='http://127.0.0.1:18082/movie-lab/'
$env:MOVIE_TEST_OUTPUT=(Join-Path (Get-Location).Parent.FullName 'deployment/verification')
node scripts/browser-test.cjs
```

可以通过 `PLAYWRIGHT_MODULE` 指定 Playwright 模块绝对路径，通过 `CHROME_PATH` 指定 Chrome 可执行文件。脚本连接的是 Helios 应用，创建并在成功后删除自己的测试数据，检查登录、CSRF、校验、64 位整数精度、CRUD、版本冲突和两个浏览器会话间的自动同步。

Payara 配置依据：[官方命令行参数文档](https://docs.payara.fish/community/docs/6.2023.9/Technical%20Documentation/Payara%20Micro%20Documentation/Payara%20Micro%20Configuration%20and%20Management/Micro%20Management/Command%20Line%20Options/Command%20Line%20Options.html)。本次实际执行结果另见本目录的验收记录。
