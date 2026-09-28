# Helios 部署验收 — 2026-09-22

结论：从当前源码在学校服务器完成构建、部署和测试，服务通过 SSH 隧道可用。

| 项目 | 实际结果 |
|---|---|
| 远程目录 | `/home/studs/s407960/is-lab1-4101` |
| 数据库 | 学院 `pg:5432/studs`，PostgreSQL 18.3 |
| 环境 | FreeBSD 14.5-STABLE、Java 21、Maven 3.8.4、Payara Micro 6.2025.1 |
| Maven | `clean verify`，BUILD SUCCESS |
| 集成测试 | 32 项，0 failures，0 errors，0 skipped |
| 浏览器与 API | 16 项，全部通过；本机 Chrome 经 SSH 隧道连接 Helios |
| HTTP 监听 | `127.0.0.1:40796`，不直接绑定外网地址 |
| 重启验证 | 停止、启动、状态查询成功；重新登录后电影接口返回 200，数据为空 |
| 测试数据 | 测试表已清理；浏览器创建的电影、坐标已删除 |
| 既有表 | 原 12 张表仍在，未执行针对它们的修改或删除 |
| 报告编码 | 41 个报告和应用文本文件通过 UTF-8 检查 |

## 证据

- [JUnit 摘要](verification/evidence/ru.itmo.movie.MovieServiceTest.txt)
- [JUnit XML，包含 32 个测试名与耗时](verification/evidence/TEST-ru.itmo.movie.MovieServiceTest.xml)
- [服务器构建日志](verification/evidence/build-test.log)
- [浏览器检查结果及时间](verification/browser-results.json)
- [数据库版本、表清单及清理结果](verification/evidence/database.txt)
- [部署前表清单](verification/evidence/tables-before.txt)
- [HTTP 监听证据](verification/evidence/listener.txt)
- [部署 WAR 的 SHA-256](verification/evidence/war.sha256)
- [界面截图](verification/ui-table.png)、[关联对象详情](verification/ui-details.png)、[特殊操作](verification/ui-operations.png)

集成测试覆盖字段校验、数据库约束、精确筛选、分页、空值排序、64 位整数、时区日期、级联删除、五项特殊操作、奖励溢出回滚、并发无丢失更新和版本修订。浏览器检查覆盖认证、CSRF、输入错误、详情、CRUD、过期版本冲突以及两个独立会话之间的自动同步。

## 部署时修复的问题

1. 账号不能新建 schema，且已有同名业务表：使用 ORM XML 覆盖表名，将正式表和测试表分别隔离为 `lab1_4101_`、`lab1_4101_test_` 前缀。
2. Maven 首次下载三个依赖遇到 TLS 握手中断：用服务器 curl 从同一 Maven Central HTTPS 地址补齐依赖后，重新构建成功。
3. Surefire 子 JVM 按整机内存申请过大堆：显式配置最大堆 384 MiB、最大 Metaspace 256 MiB、2 个处理器。
4. FreeBSD `ps` 默认截断命令行，导致管理脚本误报未运行：增加 `-ww`，并验证状态查询、停止、重新启动。

Payara 日志中出现 EclipseLink 的 JMX MBean 注册警告；数据库操作与全部应用测试正常，不能据此声称日志完全无警告。未开展工业负载测试、Docker 验证或自动开机启动配置。

俄语 LaTeX 报告已补充本次 Helios 验证结果，保留 GitHub 链接占位，不加入源码清单。本次更新未重新编译 PDF。

访问、复测和重启命令见 [部署说明](README.md)。
