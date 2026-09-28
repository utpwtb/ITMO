# 12 测试、启动脚本与 Docker：如何验证自己理解正确

## 1. 先明确本轮做了什么

本轮核对源码并编写讲解，没有重新运行应用测试。已有 [JUnit 摘要](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/verification/junit-summary.txt>) 记录 2026-09-20 的 32 项测试通过；[浏览器结果](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/verification/browser-results.json>) 记录 16 项成功检查。这些是历史受测版本的证据，不是今天重新执行的结果。

## 2. 测试框架解决什么问题

如果每改一行代码都靠手动点击所有页面，很容易漏掉空集合、溢出和并发这类情况。JUnit 帮你组织测试、执行断言、报告失败，Playwright 则能实际打开浏览器执行操作。

| 类型 | 验证范围 | 本项目情况 |
|---|---|---|
| 单元测试 | 小范围逻辑，通常隔离外部系统 | 当前主测试不是纯隔离单元测试 |
| 集成测试 | 多个组件真实协作 | Java + EclipseLink + PostgreSQL |
| 端到端测试 | 从使用者入口贯穿系统 | Chrome + HTTP + 应用 + 数据库 |

类名里叫 Test 并不决定它是哪一种测试。当前 `MovieServiceTest` 连接真实数据库，所以应按集成测试理解。

## 3. JUnit 注解怎样组织执行

源码：[MovieServiceTest.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/test/java/ru/itmo/movie/MovieServiceTest.java>)。

| 注解 | 在本测试中的作用 |
|---|---|
| `@TestInstance(PER_CLASS)` | 整个类共用一个测试实例 |
| `@BeforeAll` | 建立连接、测试 schema 和 ORM 工厂 |
| `@BeforeEach` | 每项测试前清空测试数据并重置 revision |
| `@Test` | 标记一个测试用例 |
| `@AfterAll` | 关闭工厂，删除本次临时 schema |

这里共用测试类实例是为了管理较昂贵的数据库资源，不意味着测试必须依赖之前一项留下的数据。`@BeforeEach` 正是为了把每个案例恢复到可预测起点。

## 4. 测试数据为什么不会清空应用库

默认连接专用 `movie_lab_test`，创建随机的 `test_...` schema。JDBC 设置 search_path，JPA URL 设置 currentSchema，都指向这个命名空间。

测试确实包含 TRUNCATE 与 DROP SCHEMA CASCADE，因此运行时必须确认测试 URL 和权限是你为测试准备的。不要把测试命令随手指向有真实数据的共享数据库。

随机 schema 隔离的是表空间；`System.setProperty` 这类 JVM 全局配置仍是全局的，当前测试结构不等于已经适合任意多组测试在同一 JVM 中并行修改同一配置键。

## 5. 读一个断言比看绿色按钮更有用

项目测试 `awardStrictBoundary`：先创建两部电影，把第二部长度改为 121，然后 `award(120,3)`。

预期第一部 120 分钟保持原奖项，第二部增加 3。这是在证明业务条件是严格大于，不是仅证明方法“没有抛异常”。

`awardOverflowRollsBackWholeTransaction` 让一部电影接近整数上限，再统一加奖。它同时检查抛错、其他电影未发生部分提交、revision 没增长，这比只检查出现错误消息更完整。

数据库约束测试直接执行不合法 SQL，证明约束不只是 Java 校验的假象。

## 6. 浏览器测试检查了什么

源码：[browser-test.cjs](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/scripts/browser-test.cjs>)。

测试先用 API 创建必要坐标，再启动两个**独立 browser context** 并分别登录。独立 context 有各自 Cookie/会话，适合模拟两个用户会话；仅在同一 context 开两个标签页通常共享 Cookie。

测试通过第一页面表单创建电影，等待第二页面自动看到新增；然后制造旧表单冲突，检查 409 对应提示和输入保留；最后验证删除自动同步。

另有错误密码、未登录、CSRF、Long 最大值和 JavaScript 页面错误检查。它主要是功能验证，没有执行生产级压力测试或完整安全审计。

浏览器脚本目前未绑定 Maven 生命周期，须在服务启动后单独运行。脚本成功时删除自己的测试电影和坐标；中途失败时这些数据可能留下，不能假定 finally 已完成全部业务数据清理。

## 7. 从启动脚本读懂本地环境

入口：[start-local.ps1](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/scripts/start-local.ps1>)。以下命令在项目目录运行，前提是已安装 JDK、Maven、PostgreSQL，且没有需要复用的同端口实例：

```powershell
Set-Location 'C:\develop\NOTE_UTP\StudyNote\5 Information Systems\Lab\Lab1\movie-lab'
.\scripts\start-local.ps1
```

如果实验端口被已启动的实例占用，先确认该实例用途；也可给这个新练习实例选择另一组端口：

```powershell
.\scripts\start-local.ps1 -DatabasePort 55442 -HttpPort 18082
```

脚本依次完成：建立 `.runtime` → 初始化专用 PostgreSQL 集群 → 启动数据库 → 创建应用库和测试库 → 首次执行 schema.sql → `mvn verify` → 下载 Payara → 启动 WAR。

脚本不会给已存在表自动做完整迁移；它检查 movie 表是否已存在后决定是否初始化。将来修改 schema.sql，不代表旧数据库会自动同步结构。

如果历史实验实例使用 `Lab1/tools/pgdata`，而新脚本使用 `movie-lab/.runtime/pgdata`，它们是不同数据目录。不能只因为端口相同就当成同一个集群。

## 8. 配置优先级与常见错误

`Database.config()` 的读取顺序：Java `-D` 系统属性 → 环境变量 → 默认值。测试的 user/password 则直接读取相应系统属性，不能笼统说所有测试配置都支持相同环境变量路径。

| 现象 | 优先检查 |
|---|---|
| connection refused | PostgreSQL 是否启动、端口是否一致 |
| relation does not exist | 是否执行了 DDL、schema 是否正确 |
| 找不到 AppState | 是否插入 `app_state` 的 id=1 初始化行 |
| 401 | 登录会话是否存在/过期 |
| 403 | 修改请求是否附带当前 csrf |
| 409 | version 是否过期；再看服务端数据库异常日志 |
| Maven 下载失败 | 仓库设置、网络、缓存可写性 |
| 页面不是新代码 | 是否重新打包并重新部署正确 WAR |

## 9. Docker 从零理解

镜像（образ）是运行环境与应用文件的打包模板；容器（контейнер）是镜像启动出来的进程环境；volume（том）用于持久保存数据库数据。容器不是把数据库“编译进 Java”。

当前 [Dockerfile](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/Dockerfile>) 使用两阶段构建：Maven 阶段产出 WAR，再复制到 Payara 镜像。Docker 构建使用 `-DskipTests`，不能把成功构建镜像当成已经运行全部测试。

[compose.yaml](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/compose.yaml>) 定义 database 与 app 两个服务。容器中的 JDBC 主机是服务名 `database`，因为容器内的 localhost 指当前容器本身。PostgreSQL volume 保存数据，初始化 SQL 通常只在新数据目录初始化时执行。

历史验收没有实际启动 Docker Engine，也没有连接学院 `pg/studs`。这些部署配置可以学习，但不要宣称已经验证。

## 检查题

1. `mvn verify` 是否会自动启动浏览器测试？
2. 为什么要直接执行一次错误 SQL？
3. Docker 中 app 的 localhost 是否就是 database 容器？

参考答案：本 POM 没有绑定它，所以不会；验证数据库独立约束；不是，应使用服务名连接。
