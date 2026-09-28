# 15 中俄术语、注解与源码导航

## 中俄技术术语

| 中文 | English / API | 俄语常见表达 |
|---|---|---|
| 客户端 / 服务端 | client / server | клиент / сервер |
| 请求 / 响应 | request / response | запрос / ответ |
| 依赖注入 | dependency injection | внедрение зависимостей |
| 控制反转 | inversion of control | инверсия управления |
| 作用域 | scope | область видимости |
| 受管理组件 | managed bean | управляемый бин |
| 实体 | entity | сущность |
| 持久化上下文 | persistence context | контекст персистентности |
| 对象关系映射 | ORM | объектно-реляционное отображение |
| 主键 / 外键 | primary / foreign key | первичный / внешний ключ |
| 约束 | constraint | ограничение |
| 事务 | transaction | транзакция |
| 提交 / 回滚 | commit / rollback | фиксация / откат |
| 悲观 / 乐观锁 | pessimistic / optimistic locking | пессимистическая / оптимистическая блокировка |
| 丢失更新 | lost update | потерянное обновление |
| 级联删除 | cascade delete | каскадное удаление |
| 分页 | pagination | пагинация |
| 完整匹配 | exact match | полное совпадение |
| 序列化 | serialization | сериализация |
| 会话 | session | сессия |
| 部署 | deployment | развёртывание |

## 按所属机制理解注解

| 机制 | 注解 | 在本项目中要记住什么 |
|---|---|---|
| CDI | `@Inject` | 容器注入依赖，普通 new 不触发它 |
| CDI | `@ApplicationScoped` | 应用上下文共享组件，非自动线程锁 |
| CDI | `@RequestScoped` | 当前 HTTP 请求上下文中的组件 |
| 生命周期 | `@PostConstruct` / `@PreDestroy` | 初始化和销毁回调 |
| REST | `@ApplicationPath` / `@Path` | 组合应用路径和资源路径 |
| REST | `@GET` / `@POST` / `@PUT` / `@DELETE` | 匹配 HTTP 方法 |
| REST | `@PathParam` / `@QueryParam` | 路径片段和查询参数 |
| REST | `@Produces` / `@Consumes` | 输出和输入媒体类型 |
| REST | `@Provider` | 注册过滤器、异常映射等扩展 |
| REST | `@Context` | 注入请求环境等上下文对象 |
| JPA | `@Entity` / `@Table` | 实体与表映射 |
| JPA | `@Id` / `@GeneratedValue` | 主键及生成方式 |
| JPA | `@ManyToOne` / `@JoinColumn` | 关联及外键列 |
| JPA | `@Version` | 实体版本与乐观并发控制 |
| JPA | `@Enumerated(STRING)` | 存枚举名称，而不是序号 |
| JPA | `@Convert` / `@Converter` | 属性与数据库列的转换 |
| JPA | `@PrePersist` | 实体即将持久化时的回调 |
| Validation | `@NotNull` / `@Positive` / `@Size` / `@Max` | 校验对象值，不等于执行 DDL |
| JSON-B | `@JsonbTypeSerializer` | Java 值怎样输出为 JSON |
| JUnit | `@Test` / `@BeforeEach` 等 | 测试方法与生命周期 |

同样以 `@` 开头，不表示由同一个框架处理。查 import 是识别机制的好办法。

## 从问题定位源码

| 想解决的问题 | 从哪里看 |
|---|---|
| 依赖和编译目标 | [pom.xml](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/pom.xml>) |
| 数据实际有哪些约束 | [schema.sql](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/database/schema.sql>) |
| 电影映射与生成字段 | [Movie.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/domain/Movie.java>) |
| ORM 提供者和缓存 | [persistence.xml](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/resources/META-INF/persistence.xml>) |
| 事务为什么会回滚 | [Database.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/persistence/Database.java>) |
| CRUD、分奖和分页 | [MovieService.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/service/MovieService.java>) |
| 一个 URL 调哪个方法 | [MovieResource.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/MovieResource.java>) |
| 登录状态怎么产生 | [AuthResource.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/AuthResource.java>) |
| 为什么返回 401/403 | [AuthFilter.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/AuthFilter.java>) |
| 异常怎样变成 JSON | [ErrorMapper.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/ErrorMapper.java>) |
| 保存按钮和轮询 | [app.js](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/webapp/app.js>) |
| 自动化证明了哪些边界 | [MovieServiceTest.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/test/java/ru/itmo/movie/MovieServiceTest.java>) |
| 双会话怎么测试 | [browser-test.cjs](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/scripts/browser-test.cjs>) |
| 从零启动环境 | [start-local.ps1](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/scripts/start-local.ps1>) |

## 五个很值得设断点的位置

1. `AuthFilter.filter`：请求还没有进入业务，看看会话和 token。
2. `MovieResource.create`：确认 URL、请求体解析后的参数。
3. `MovieService.save`：观察字符串如何转为目标类型，以及关联对象如何查到。
4. `Database.write` 的 commit 前：确认事务里究竟做了哪些动作。
5. `ErrorMapper.toResponse`：看到一个异常最后怎样成为 HTTP 状态和消息。

浏览器的 Network 面板与 Java 调试器配合，能完整观察前后端链路。不建议第一次学习就从生成的 SQL 内部调用栈一路深入驱动实现。

## 参考资料与使用方式

技术版本以工作区配置为准，不追逐最新版。本次核对官方规范入口用于确认名词与技术边界；项目行为的主要依据是实际源码与历史测试记录。

- [Jakarta EE 10](https://jakarta.ee/specifications/platform/10/)：平台规范与 API。
- [CDI 4.0](https://jakarta.ee/specifications/cdi/4.0/)：上下文和依赖注入。
- [Jakarta Persistence 3.1](https://jakarta.ee/specifications/persistence/3.1/)：持久化规范入口。
- [Maven 生命周期](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)：构建阶段与插件目标。
- [PostgreSQL 17 约束](https://www.postgresql.org/docs/17/ddl-constraints.html)：NOT NULL、CHECK、UNIQUE、外键等。
- [Jakarta Data 1.0](https://jakarta.ee/specifications/data/1.0/)：答辩中的仓库式访问抽象。
- [Spring Framework 概述](https://docs.spring.io/spring-framework/reference/overview.html)：与 Jakarta EE 的比较背景。

先读教程建立问题意识，遇到具体疑问再翻规范。不要用规范里“允许的所有能力”反推本实验已经实现了那些能力。
