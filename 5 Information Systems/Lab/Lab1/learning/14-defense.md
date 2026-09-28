# 14 答辩准备：技术比较、俄语表达与实现边界

对应 [原题最后的答辩问题](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/Lab1.md>)。先用中文理解，再练习俄语说法。下面的短答是表达模板，不是要求逐字背诵。

## 1. 设计模式与架构模式

架构模式描述系统较大范围的职责和协作；设计模式通常描述对象或组件之间反复出现的问题及解决结构。

当前是分层架构：web 接 HTTP，service 处理业务，persistence 管事务，domain 定义模型。CDI 实现依赖注入；EntityManager 的持久化上下文具有工作单元与对象身份管理等特征。

项目没有单独的 `MovieRepository` 类。不要为了套术语声称使用了一个实际上不存在的 Repository 层。`@ApplicationScoped` 也不等于你手写了 GoF Singleton 的私有构造器和全局 getter。

俄语短答：**В приложении используется многослойная архитектура. HTTP-ресурсы отделены от бизнес-логики, а транзакции вынесены в компонент Database. Зависимости передаются через CDI.**

追问：业务方法为什么不直接读取 HttpServletRequest？因为它应能被独立测试或其他入口调用，不应把计算规则绑定在 HTTP 环境中。

## 2. Jakarta EE 平台与组件

Jakarta EE 是多项规范组成的平台。当前使用 REST、CDI、Servlet、Persistence、Validation、JSON-B。Payara 提供运行环境；EclipseLink 提供 ORM 实现。

EJB、JMS、Faces 等属于相关企业 Java 技术，但当前代码没有用 EJB 实现业务、没有 JMS 消息队列、没有 Faces 页面。列举平台能力时要区分“平台有”和“本实验用”。

俄语短答：**Jakarta EE задаёт стандартные API для серверных приложений. В моей работе используются CDI, REST, Servlet, Persistence, Validation и JSON-B; приложение развёртывается в Payara.**

## 3. Managed Beans 与 CDI Beans

受管理组件由容器处理一定范围的生命周期与协作；CDI 提供依赖注入、上下文作用域等能力。当前使用 `@ApplicationScoped`、`@RequestScoped` 和 `@Inject`，不是旧 JSF `@ManagedBean`。

俄语短答：**MovieService и Database имеют область ApplicationScoped, а REST-ресурсы — RequestScoped. CDI создаёт компоненты и разрешает их зависимости. Управляемая JPA-сущность — другое понятие: она связана с контекстом персистентности.**

追问：全局作用域为什么不会共享一个 EntityManager？EntityManager 是每次数据库工作创建的局部对象，共享的是工厂。

## 4. ORM、Hibernate 与 EclipseLink

ORM 解决对象和关系表之间的映射。Hibernate ORM 和 EclipseLink 都提供 JPA 实现，也各有实现特定功能；使用相同标准 API 有利于减少绑定，但并不保证替换提供者后所有行为、SQL 和配置完全一致。

当前显式配置 EclipseLink。测试依赖中的 Hibernate Validator 实现 Bean Validation，不能据此说 ORM 是 Hibernate。

俄语短答：**JPA является спецификацией, а EclipseLink и Hibernate ORM — её реализациями. В проекте выбран EclipseLink. Hibernate Validator в тестах проверяет ограничения объектов и не заменяет ORM-провайдер.**

## 5. Jakarta Persistence

应该能解释 Entity、ID、关联映射、EntityManager、持久化上下文、JPQL、事务和 version。这些概念共同使“修改对象字段”最终成为数据库写入。

当前采用 RESOURCE_LOCAL，由 Database 显式 begin/commit/rollback。不能说是因为类上用了 `@Transactional`，因为当前代码没有这样实现。

俄语短答：**EntityManager управляет состоянием сущностей и выполняет запросы. Изменения управляемых объектов синхронизируются с БД. В проекте граница локальной транзакции явно задана в Database.write().**

## 6. Jakarta Data

Jakarta Data 是面向仓库式数据访问的规范，提供更高层的数据访问抽象。理解重点是减少某些常见数据访问代码，不是认为它让数据库、ORM 或事务从此不存在。它与 JPA 的职责并不完全相同，具体支持取决于提供者。[Jakarta Data 1.0 官方入口](https://jakarta.ee/specifications/data/1.0/)

本实验没有 Jakarta Data 的 repository 接口，也没有相应实现依赖，不能把 `Database` 类说成 Jakarta Data。

俄语短答：**Jakarta Data описывает более высокий уровень доступа к данным через репозитории. В данной работе этот API не используется: запросы выполняются непосредственно через JPA EntityManager.**

## 7. Spring 与 Java EE / Jakarta EE

Spring Framework 是应用开发框架，核心有 IoC 容器和依赖注入等能力。Jakarta EE 是规范平台；两者在目标上有交集，也可以使用一些相同的标准 API。不能简单说成“Spring 只能独立运行，Jakarta 只能传统大服务器运行”。[Spring Framework 官方概述](https://docs.spring.io/spring-framework/reference/overview.html)

本项目选择 Jakarta/CDI 是因为实验要求。`@Inject`、`@Path` 与 Spring 的 `@Autowired`、`@RestController` 不是只换 import 就完全等价，组件发现、HTTP 集成与生命周期需要对应框架运行环境。

俄语短答：**Spring Framework предоставляет собственный контейнер и инфраструктуру приложения. Jakarta EE определяет набор стандартных API. В работе используется Jakarta EE, поэтому компоненты управляются CDI, а HTTP-интерфейс реализован через Jakarta REST.**

## 8. Spring Boot

Spring Boot 基于 Spring 生态，帮助自动配置、管理常见依赖组合和启动应用。它不是另一种 ORM，也不意味着不需要理解底层 Spring。

本实验启动的是 Payara Micro 并部署 WAR，没有 Spring Boot 主类、starter 或自动配置。不能把“一个 java -jar 命令能启动”当成“它就是 Boot”的证据。

俄语短答：**Spring Boot упрощает настройку и запуск Spring-приложений. Мой проект не использует Spring Boot: WAR развёртывается в Payara Micro.**

## 9. Spring Data

Spring Data 是一组数据访问项目。Spring Data JPA 利用 JPA 并提供 repository 等抽象；它不是替代 JPA 的数据库引擎。下层仍可能用 Hibernate ORM 或 EclipseLink，具体取决于配置与兼容性。

俄语短答：**Spring Data упрощает типовые операции доступа к данным. Spring Data JPA работает поверх JPA; в моём приложении используется непосредственно EntityManager, без Spring Data.**

## 10. 本实验最可能被追问的实现细节

| 问题 | 应答核心 |
|---|---|
| 你用 WebSocket 同步吗？ | 没有，是两秒轮询 revision；不保证所有网络环境下严格两秒 |
| 为什么全局锁还需要 version？ | 全局锁保护执行中的事务，version 识别用户手里的旧表单 |
| flush 后是否已提交？ | 没有，flush 同步 SQL，commit 才完成事务 |
| 为什么奥斯卡没有全部转空？ | 原题存在矛盾，按确认规则每部来源电影保留 1 个 |
| 为什么删除电影不删导演？ | 导演可以被其他电影共享，级联按依赖方向处理 |
| 平均值在哪算？ | 当前用 JPQL AVG，由数据库执行聚合，无自定义存储过程 |
| 你实现了完整用户系统吗？ | 没有，配置一个教学账号，多个独立会话使用共享集合 |
| 测试是什么时候通过的？ | 历史验收为 2026-09-20，引用对应记录；教程编写未重跑 |

## 11. 怎样诚实说明尚未覆盖的部分

明确说：Docker 配置和学院连接步骤有提供，但历史验收没有实际验证这两条环境路径；没有工业级压力测试；全局写锁、完整加载辅助对象列表属于教学规模的简化。

后续改进可以包括明确 DTO、更细的锁粒度、分页辅助列表、数据库迁移工具和细分错误响应。描述这些时使用“可以改进”，不要说成当前已具备。

## 两分钟讲述结构

先用一句话说明电影和关联对象管理；再说明浏览器、REST、CDI 服务、JPA、PostgreSQL 的链路；然后举创建或分奖的一个事务例子；最后解释 version/revision 和测试证据。能在此基础上回答细节，比背一串框架名称更有说服力。
