# 02 Maven、WAR、Jakarta EE 与 Payara

## 1. 先区分四种工作

假设你只有 JDK：它可以编译 Java，但不会自动知道去哪里下载 EclipseLink，也不会自动监听电影接口。项目因此需要构建工具、框架 API 和运行容器。

| 名称 | 本实验中的工作 | 不负责什么 |
|---|---|---|
| JDK | 编译与执行 Java；提供标准库 | 不替你定义电影接口 |
| Maven | 获取依赖、编译、执行测试、打包 | 不等于应用服务器 |
| Jakarta EE | 提供企业应用的一组规范/API | API JAR 本身不等于完整运行环境 |
| Payara Micro | 启动服务器、部署 WAR、运行受管理组件 | 不替你决定业务规则 |

Java EE 是题目使用的名称；本实现使用后续的 Jakarta EE 10，源码导入 `jakarta.*`。旧教材中的 `javax.persistence`、`javax.ws.rs` 不能直接混入本项目；但是 Java 标准库里仍存在某些合法的 `javax.*` 包，不能机械地全部替换。[Jakarta EE 10 官方规范入口](https://jakarta.ee/specifications/platform/10/)

## 2. 为什么规范和实现要分开

你调用 `List.add()` 时，真正保存元素的是 `ArrayList` 或其他具体实现。类似地，JPA 规定 `EntityManager` 的契约，EclipseLink 提供具体行为。

这个类比只用于理解“契约与实现”：Jakarta EE 是很多规范组成的平台，不只是一个 Java 接口。容器负责组合所需能力；不同规范可以有不同实现。

本项目导入 Jakarta API 来写代码；运行 WAR 时由 Payara 提供 REST、CDI 等环境。数据库对象映射由 EclipseLink 完成。

## 3. 从实际 pom.xml 读依赖

源码：[pom.xml](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/pom.xml>)。

项目节选：

```xml
<groupId>ru.itmo</groupId>
<artifactId>movie-lab</artifactId>
<version>1.0.0</version>
<packaging>war</packaging>
```

前三个值组成 Maven 项目标识。`packaging=war` 决定这是 Web 应用归档。`finalName=movie-lab` 使输出文件叫 `movie-lab.war`。

| 依赖 | 用途 | 当前 scope |
|---|---|---|
| `jakarta.jakartaee-api:10.0.0` | 编译时能识别 Jakarta 注解/API | `provided` |
| `eclipselink:4.0.5` | JPA 实现，独立测试用它访问数据库 | 默认 compile |
| `postgresql:42.7.5` | JDBC 驱动，负责 PostgreSQL 通信 | 默认 compile |
| `hibernate-validator:8.0.2.Final` | 独立测试中的 Bean Validation 实现 | `test` |
| `expressly:5.0.0` | 测试环境所需的表达式语言实现 | `test` |
| `junit-jupiter:5.11.4` | 测试框架 | `test` |

`provided` 表示编译/测试需要，部署时预期由运行环境提供，通常不打入 WAR 的依赖库目录。`test` 限于测试；没有写 scope 的普通依赖默认是 compile。

**Hibernate Validator 不等于 Hibernate ORM。** 名字中都有 Hibernate，不代表项目换了 ORM。本项目的持久化提供者仍是 EclipseLink。

## 4. Maven 命令的先后关系

```text
compile → test → package → verify
```

这些是常见阶段的简图，实际生命周期还包含更多中间阶段。调用后面的阶段，会执行之前绑定的任务。`mvn package` 默认也会先运行测试；`-DskipTests` 才跳过测试执行。本项目 Surefire 执行 `MovieServiceTest`，虽然名字叫集成测试，它仍绑定在 `test` 阶段，没有另配 Failsafe。[Maven 生命周期说明](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)

`mvn verify` 不会凭空启动 PostgreSQL：测试要连接的数据库必须先存在。也不会自动运行独立的 Playwright 脚本。`mvn deploy` 通常表示向 Maven 仓库发布构件，不是把页面发布到 Payara。

## 5. WAR 里面有什么

WAR 本质上是一种有约定结构的归档：静态页面、编译后的 Java 类、依赖 JAR 和 Web 配置放在一起。

```text
movie-lab.war
  index.html / app.js / style.css
  WEB-INF/classes/      编译后的类和 persistence.xml
  WEB-INF/lib/          需要随应用分发的依赖
  WEB-INF/web.xml
  WEB-INF/beans.xml
```

你不需要给 `MovieResource` 写 `main()`。Payara 自己有启动入口，它部署 WAR、发现资源并接收 HTTP 请求。

教学命令（先准备数据库和构建产物，路径仅示意）：

```powershell
java -jar payara-micro-6.2025.1.jar --deploy target/movie-lab.war --port 18081 --noCluster
```

`--deploy` 指定应用，`--port` 指定 HTTP 端口，`--noCluster` 关闭此学习场景不需要的集群机制。完整可用入口是 [start-local.ps1](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/scripts/start-local.ps1>)，第 12 章拆解。

## 6. 配置文件怎样配合

| 文件 | 读它的组件 | 作用 |
|---|---|---|
| `pom.xml` | Maven | 构建与依赖 |
| `persistence.xml` | JPA 引导过程 | 持久化单元、提供者、实体列表 |
| `beans.xml` | CDI 环境 | 配置受注解 Bean 的发现 |
| `web.xml` | Web 容器 | 会话超时与 Cookie 设置 |
| `schema.sql` | PostgreSQL 客户端执行 | 真正建立表、约束与索引 |
| `compose.yaml` | Docker Compose | 组织应用与数据库容器 |

当前配置没有让 ORM 自动建表，不能只创建 `Movie.java` 就期待数据库自动出现所有约束。

## 7. 版本号还要看运行环境

POM 指定 EclipseLink 4.0.5，独立 JUnit 测试使用该版本。历史部署检查发现，Payara 通过父加载器使用自带的 `4.0.1.payara-p3`。因此“POM 里有哪个版本”和“容器实际加载哪个版本”不能直接画等号。历史证据见 [验收记录](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/verification/ACCEPTANCE.md>)。

项目以 Java 17 为编译目标，历史环境使用 JDK 21 编译运行。`release=17` 是本项目的目标选择，不代表所有 Jakarta EE 10 应用都必须使用 Java 17。

## 检查题

1. 只添加 Jakarta API 依赖，能让普通 Java 程序自动出现 Web 服务吗？
2. 为什么测试中的 Validator 要自己带实现，而容器部署可以使用环境提供的能力？
3. 为什么新建数据库后仍需执行 schema.sql？

参考答案：不能，API 需要运行时实现和引导；独立测试不运行在完整 Payara 环境中；本项目的实体映射负责访问已有表，实际 DDL 由 SQL 脚本建立。
