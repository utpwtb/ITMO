# 03 CDI：对象由谁创建，依赖由谁连接

## 1. 从手动 new 开始理解

教学示意：如果没有容器，你可能这样组装对象：

```java
Database database = new Database();
database.init();
MovieService service = new MovieService(database);
```

这正接近当前测试采用的方式。你负责先创建数据库组件，再交给业务组件，还要记得最后关闭。

服务端部署则让 CDI 处理符合规则的组件创建与依赖装配。CDI 是 Contexts and Dependency Injection；中文可理解为上下文与依赖注入，俄语常说 **внедрение зависимостей**。

## 2. IoC 与 DI 分别指什么

控制反转（IoC，инверсия управления）描述一种变化：组件的创建和调用时机交给框架控制。依赖注入（DI）是把组件需要的依赖从外部交给它，而不是让它自己到处寻找、创建。

项目节选：[MovieService.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/service/MovieService.java>)。

```java
@ApplicationScoped
public class MovieService {
    @Inject
    Database db;
}
```

`@Inject` 声明这里需要一个 `Database`。容器根据类型等规则解析依赖并提供可用引用；对于正常作用域，经常通过代理访问对应上下文实例。业务方法只需要使用 `db`，不需要知道它的装配细节。

注解（аннотация）本身是元数据。`@Inject` 不会在任意 Java 程序中自动执行赋值。你自己 `new MovieService()` 又没设置 `db`，仍可能遇到空指针。

CDI 的组件管理与依赖注入属于规范定义的能力；本项目只是其中一个简单用法。[CDI 4.0 官方入口](https://jakarta.ee/specifications/cdi/4.0/)

## 3. 为什么要有作用域

作用域（область видимости / scope）回答：实例在什么上下文内存在、不同调用怎样访问它。

| 当前组件 | 注解 | 本项目中的意义 |
|---|---|---|
| `MovieResource` | `@RequestScoped` | 处理一次 HTTP 请求的资源实例 |
| `AuthResource` | `@RequestScoped` | 当前请求中的登录操作 |
| `MovieService` | `@ApplicationScoped` | 应用范围的业务组件 |
| `Database` | `@ApplicationScoped` | 应用范围管理 EntityManagerFactory |

`@ApplicationScoped` 不表示每个请求都串行执行，也不会自动给方法加互斥锁。多个请求可以同时进入同一个服务组件。因此不能在字段里放“当前正在编辑的电影”这种每个用户都不同的临时值。

本项目把 `EntityManager` 放在方法局部变量里，为每次数据库工作单独创建；共享的是可被并发使用的 `EntityManagerFactory`。这比简单地把整个数据库访问对象做成一个全局可变状态更可靠。

## 4. 生命周期：初始化和销毁

源码：[Database.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/persistence/Database.java>)。

```java
@PostConstruct
public void init() {
    factory = Persistence.createEntityManagerFactory("movies", ...);
}

@PreDestroy
public void close() {
    if (factory != null) factory.close();
}
```

这是带省略号的教学节选，不可直接编译。`@PostConstruct` 在容器完成注入后调用，适合使用已准备好的配置创建工厂；`@PreDestroy` 在受管理实例销毁前做资源清理。应用作用域的实例可能在首次需要时才真正初始化，不必假定所有 Bean 都在服务器启动瞬间创建。

测试手动 `new Database()` 时，JUnit 测试代码显式调用 `init()` 和 `close()`；普通 `new` 不会自动触发这些 CDI 生命周期回调。

## 5. 三个容易混淆的“Bean”

| 术语 | 应怎样理解 |
|---|---|
| JavaBean | 一类 Java 对象约定，常见无参构造和访问方法 |
| CDI Bean | 由 CDI 发现、管理上下文并注入依赖的组件 |
| JPA managed entity | 被某个持久化上下文跟踪的实体对象 |

`MovieService` 是 CDI 管理组件；从 `EntityManager.find()` 得到的 `Movie` 可以是 JPA 的 managed 实体。它们的“managed”指向不同机制。

题目说 Managed Beans，本实现采用 CDI Bean，没有使用旧 JSF `@ManagedBean`，也没有用 JSF 的 XHTML 组件构造页面。答辩要说明实际采用的形式。

## 6. 测试为什么保留第二个构造方法

`MovieService` 既有无参构造，也有 `MovieService(Database db)`。后者让独立测试手动传入已经初始化的数据库组件。

这个带参构造没有 `@Inject`。因此不要讲成“容器在这里执行构造器注入”。实际部署采用的是字段注入；测试采用的是显式构造传参。

## 动手观察

只阅读 [测试 setup 方法](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/test/java/ru/itmo/movie/MovieServiceTest.java>)，找出 `new Database()`、`db.init()`、`new MovieService(db)`。将它们与服务器中的 `@Inject` 对照，你就能看到两种装配方法访问的是同一套业务逻辑。

## 检查题

1. `@ApplicationScoped` 能代替数据库锁吗？
2. 创建 JPA 实体一定要用 CDI 吗？
3. 为什么测试没有容器也能调用服务？

参考答案：不能；实体可以通过普通构造或反射创建，再交给 JPA 管理；测试主动创建依赖并传给服务，业务方法不依赖 HTTP 才能执行。
