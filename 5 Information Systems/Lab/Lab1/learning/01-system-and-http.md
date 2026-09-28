# 01 从需求到一个 Web 系统

## 1. 为什么 `ArrayList<Movie>` 不够

你已经会用 Java 创建对象：`Movie movie = new Movie()`。假设用一个列表保存全部电影，在本机控制台增加、删除，它只能满足非常小的一部分题目。

关掉进程，列表通常就没了；第二个人启动程序，会得到另一份列表；两个人同时给一部电影加奖项，彼此无法看见。这三个问题分别引出**持久化、共享服务端和并发控制**。

持久化（персистентность）是让数据不依赖某次 Java 进程的生命。客户端（клиент）是用户使用的浏览器；服务端（сервер）接收不同客户端请求，统一执行规则。PostgreSQL 负责持久保存共享数据。

## 2. 浏览器和 Java 不在同一个执行环境

用户打开网页时，Payara 返回 HTML、CSS、JavaScript。HTML 定义输入框、按钮、表格；CSS 控制外观；JavaScript 处理点击并发送请求。这些 JavaScript 在浏览器里执行。

Java 的 `MovieService` 在服务器 JVM 中执行。浏览器不能直接调用它，也不能直接访问服务器上的 `EntityManager`。两边用 HTTP 传递数据：JavaScript 发一个请求，服务器解析后调用 Java 方法，再返回响应。

即使所有程序都运行在同一台电脑上，这仍然是通过网络协议连接的不同进程。`localhost` 只是表示本机，不会让它们变成一个进程。

## 3. 拆开一个 URL

教学示例：

```text
http://localhost:18081/movie-lab/api/movies?page=0&size=10
```

| 部分 | 意义 |
|---|---|
| `http` | 通信协议 |
| `localhost` | 目标主机是本机 |
| `18081` | Payara 的 HTTP 监听端口 |
| `/movie-lab` | 当前 WAR 部署对应的上下文路径 |
| `/api` | `ApiApplication` 定义的接口前缀 |
| `/movies` | 要访问的资源 |
| `page=0&size=10` | 查询参数：第 0 页，每页 10 个 |

数据库使用另一个端口，例如本实验本地脚本默认的 `55441`。浏览器访问 `18081`，Java 再连接 `55441`；这两个端口承担不同职责。

## 4. HTTP 请求包含什么

一个请求主要由**方法、地址、请求头和可选的请求体**组成。方法表达意图，请求体承载需要保存的数据。

| 本项目的方法 | 示例地址 | 意图 |
|---|---|---|
| GET | `/api/movies/7` | 读取 ID 为 7 的电影 |
| POST | `/api/movies` | 创建电影 |
| PUT | `/api/movies/7` | 修改电影 |
| DELETE | `/api/movies/7?version=2` | 删除指定版本的电影 |

HTTP 响应还包括状态码。200 是正常结果，201 表示创建成功；400 表示输入问题，401 表示未通过身份验证，403 在本实验中常见于 CSRF 校验失败，404 表示对象/地址不存在，409 表示冲突，500 表示服务端没有正常处理的内部问题。

这些数字不是业务返回值的替代品。例如创建响应既有 201，又有新电影的数据；错误响应既有 400，又有具体的俄语错误说明。

## 5. JSON 是数据表示，不是 Java 对象本身

教学示例：

```json
{"name":"Учебный фильм","oscarsCount":"3","coordinates":"1"}
```

JSON 中有键、值、数组等结构。它没有 Java 类的方法，也不会自动携带数据库连接。服务端把这段文本解析成 `Map<String,Object>`，再检查、转换成实体字段。

这里数字使用字符串是有意的：本项目表单先保留输入文本，服务端负责转成 `int`、`long` 等精确类型。`coordinates` 是已存在的坐标记录 ID，不是用户任意提交的一整个新坐标对象。

## 6. 把题目拆成可以实现的层

| 题目要求 | 实现责任 |
|---|---|
| 独立窗口和表格 | HTML 的 dialog/table 与 JavaScript |
| 通过 ID 查询、创建、更新、删除 | REST 资源接收请求，服务层处理 |
| 复用人员和坐标 | 数据库外键 + 服务层按 ID 查找 |
| 正数、非空、唯一 | 类型转换 + Bean Validation + 数据库约束 |
| 特殊操作 | `MovieService` 的业务方法 |
| 别的用户自动看到变化 | 数据库 revision + 浏览器轮询 |
| 避免同时修改相互覆盖 | 写事务串行化 + 对象 version |

分层（многослойная архитектура）的价值在于：改表格样式，不需要改事务；调整奥斯卡分配，不需要改 HTTP 登录。它是职责划分，不要求每一层运行在独立机器上。

## 7. 先认识实际目录

打开 [应用目录说明](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/README.md>)，再对照：

```text
movie-lab/
  pom.xml                  构建与依赖
  database/schema.sql      PostgreSQL 建表规则
  src/main/java/.../
    domain/                持久化对象与枚举
    persistence/           EntityManager 与事务
    service/               业务规则
    web/                   HTTP 接口、认证、错误映射
  src/main/resources/      ORM 配置
  src/main/webapp/          浏览器界面与 Web 配置
  src/test/java/            Java 集成测试
  scripts/                 启动与浏览器测试
```

## 检查题

1. 为什么不能只在 HTML 上写 `min="1"` 就保证数据正确？
2. 用户关闭浏览器后，电影为什么不会消失？
3. `POST /api/movies` 与 `new Movie()` 是同一个操作吗？

参考答案：客户端限制可以被绕过，服务端和数据库仍须检查；电影已提交到 PostgreSQL，不靠浏览器内存保存；POST 是网络请求，服务器处理它时才可能创建对象、保存并返回结果，单独 `new` 不会写数据库。

下一章：[构建和运行环境](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/learning/02-build-and-runtime.md>)。
