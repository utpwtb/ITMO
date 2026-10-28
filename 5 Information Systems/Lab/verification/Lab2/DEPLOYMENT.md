# Helios 实际部署与交接

2026-10-28（Europe/Moscow）。四项界面修订已在 Helios 重新构建并部署，最新验证 PID **65452**。此前真实重启验收 PID 44732，日志显示其在05:00退出，原因未由应用日志确定；续作时曾恢复为 PID49365。

| 项目 | 实际值 |
|---|---|
| SSH | s407960@helios.cs.ifmo.ru:2222 |
| 项目 | /home/studs/s407960/is-lab2-4101 |
| HTTP | 127.0.0.1:40797/movie-lab/ |
| 正式数据库 | pg:5432/studs，schema s407960，lab2_4101_前缀 |
| 测试数据库 | 同schema，lab2_4101_test_前缀；正式表与压测数据分离 |
| 当前 WAR | target/movie-lab.war；SHA256 867545d9dbbf8d18e9d224e3b29b0c7387ab49458b9f8ed44d7421cbec3f87f4 |
| 配置 | movies-helios；显式READ COMMITTED；AppState锁；lock_timeout10000ms；@Version及客户端版本 |
| 日志 / PID | .runtime/payara.log / .runtime/payara.pid |
| 当前本地WAR副本 | ui-review/movie-lab.war，已核对同一哈希 |

当前修订只改变 app.js、index.html、style.css、ui-text.js。服务器 Maven package 成功；WAR 其余所有条目逐字节匹配原验证版本 `cf386061ed67f25abac1f84cf13b61fdcb4a988dddbfe3363c81e670365d0576`，包含全部 Java 类、依赖、数据库映射。140 项 Java 测试与1640个 JMeter 目标请求属于该原版本，本次没有重跑全套测试。新版本的构建、条目哈希、正式领域快照不变与实际静态资源核对保存在 `ui-review/deployment.json`；浏览器验证见 `browser/final-ui-checks.json`。首次探测过早得到临时503并回退的真实记录也保留在 ui-review/。

文件选择控件固定俄语，移除事务说明、历史范围说明及刷新按钮；历史保持两秒轮询。真实浏览器提交产生失败操作10；另一独立HTTP会话产生操作11，打开的历史页无点击/重载自动出现该行，revision仍为8。管理员上一页/下一页均通过。正式电影、人、坐标、地点不增加。

```sh
cd ~/is-lab2-4101
python3.11 scripts/helios.py status
python3.11 scripts/helios.py stop
# 确认旧进程结束后启动
MOVIE_ISOLATION="READ COMMITTED" python3.11 scripts/helios.py start
```

停止脚本核对PID对应本部署Java进程，启动脚本拒绝旧实例仍存在；不会停止实验一。启动前在确认旧实例结束后恢复遗留RUNNING。若进程日后被外部终止，按上述命令重建；此交付不增加定时重启任务。

本地建立隧道后访问：

```powershell
ssh -N -L 18083:127.0.0.1:40797 -o ExitOnForwardFailure=yes -p 2222 s407960@helios.cs.ifmo.ru
```

地址为 [远程应用的本地隧道入口](http://127.0.0.1:18083/movie-lab/)。也可使用 scripts/lab2-remote.py tunnel 18083 40797。隧道须保持运行；关闭本地进程后需要重建。

Web允许自行注册。两普通用户和两管理员的验收账号保存在服务器私有 `.runtime/lab2-users.json`；不复用SSH密码，不在仓库/报告公布。为其他已注册用户名配置管理员使用 `MOVIE_ADMIN_USER=exact_name python3.11 scripts/helios.py admin`。注册不能自授ADMIN。

可复跑完整步骤见 `../../movie-lab/README.md`、`../../movie-lab/jmeter/README.md`。旧数据库迁移使用 `helios.py migrate`；新库才使用init（存在表即拒绝）。JUnit与Web/JMeter不可同时占用测试表，备份恢复只作用于指定七张测试表。私有快照、.pgpass、加密SSH凭据和会话Token未进入交付归档。

原始服务器证据归档：lab2-server-evidence.tar.gz，SHA256 `7d5a228d1ab60cfbc68e3d62e42d5f56a4e12fe8974b3c88f66e16e31cd8b3d4`；解包于server/，10868个原始文件逐项匹配。resume/是上午续作后的补充证据，原始归档不被改写。恢复测试记录7的错误摘要已局部翻译为俄语，状态/时间/数量和领域对象不变；新增F03补测记录8及使用独立runId的复核记录9明确属于新测试。
