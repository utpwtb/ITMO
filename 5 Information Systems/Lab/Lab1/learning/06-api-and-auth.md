# 06 REST、JSON、登录会话与错误响应

## 1. URL 怎样找到 Java 方法

源码：[ApiApplication](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/ApiApplication.java>)、[MovieResource](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/MovieResource.java>)。

```java
@ApplicationPath("/api")
public class ApiApplication extends Application { ... }
```

这是教学节选。应用前缀来自 `@ApplicationPath`；资源路径来自 `@Path`；HTTP 方法来自 `@GET`、`@POST` 等。Jakarta REST（旧称 JAX-RS）框架负责路由到匹配方法。

项目中的读取接口节选：

```java
@GET
@Path("{kind:movies|people|coordinates|locations}/{id}")
public Object get(@PathParam("kind") String kind, @PathParam("id") long id) {
    return service.get(kind, id);
}
```

| 部分 | 解释 |
|---|---|
| `kind` 后的正则 | 限制只能访问四类资源 |
| `{id}` | 从路径中提取标识 |
| `@PathParam` | 把路径片段绑定为参数 |
| `long id` | 框架需要把文本转换为 long |
| `service.get()` | 路由层把业务工作交给服务层 |

列表接口使用 `@QueryParam` 读取 `?page=0` 这类参数；`@DefaultValue` 指定缺省值。创建接口的 `Map<String,Object>` 接收 JSON 对象请求体。路径参数、查询参数、请求体是三种不同来源。

## 2. 为什么方法能返回 Map 或 Movie

`@Produces(APPLICATION_JSON)` 声明输出 JSON，`@Consumes(APPLICATION_JSON)` 声明接收 JSON。容器中的消息体处理机制使用 JSON-B 等能力处理对象与 JSON 的转换。

`return movie` 并不是把 JVM 内存地址传给浏览器，而是按序列化规则输出字段数据。创建接口用 `Response.status(201).entity(...).build()` 同时设置状态码与响应体。

`LongJsonSerializer` 专门保护大整数：Java long 的精确范围大于 JavaScript Number 能精确表示的整数范围。因此预算可能输出为 `"9223372036854775807"`。

## 3. REST 资源为什么薄

如果在资源方法里写 SQL、分奖算法和事务，再在其他界面复用这些操作就很困难。当前资源主要做参数接收和服务调用，业务在 `MovieService`。

当前 PUT 实际允许只提供部分字段，未给出的字段保留。它更接近部分更新语义；读代码时不能因为看到 `@PUT` 就断言它实现了严格的整资源替换。更规范的进一步设计可以采用 PATCH 或明确更新 DTO。

## 4. HTTP 无状态，登录状态放在哪里

“HTTP 无状态”指协议本身不会自动记住上次谁登录。应用通过会话（сессия）建立联系：服务器保存会话数据，浏览器随请求发送会话 Cookie。

当前流程，见 [AuthResource](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/AuthResource.java>)：

```text
POST /api/auth + 用户名密码
→ 服务端比较配置的账号
→ 失效旧会话，创建新会话
→ 在会话中保存 user 和随机 csrf
→ 返回登录状态与 csrf
→ 浏览器后续同源请求自动携带会话 Cookie
```

默认账号是学习用途的 `student / student`，可用环境变量替换。没有用户注册、用户表、角色权限或密码哈希存储流程。多用户演示使用多个独立会话，不是已经实现了完整账户管理系统。

`@RequestScoped` 资源对象的生命周期只有请求长度；登录状态放在 HttpSession，所以不会随着一次资源调用结束而消失。

## 5. Session 与 CSRF token 为什么都需要

会话 Cookie 用于识别会话，但浏览器可能在访问另一个站点时自动带上目标站点 Cookie。CSRF（межсайтовая подделка запроса）关注这种跨站诱导修改问题。

本项目的 [AuthFilter](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/AuthFilter.java>) 对登录状态和修改操作做前置校验：

| 情况 | 处理 |
|---|---|
| GET/POST auth | 允许访问登录状态或提交登录 |
| 其他 API 没有有效会话 | 返回 401 |
| 修改操作缺少正确 `X-CSRF-Token` | 返回 403 |
| 通过验证 | 继续调用资源方法 |

前端把服务器返回的 csrf 保存于页面状态，并放入请求头。它不等于密码，也不取代会话。HttpOnly Cookie 限制 JavaScript 读取会话 Cookie，但并不等于“所有安全问题都解决了”。

会话配置默认 30 分钟不活动超时；不过界面每两秒轮询也是请求，可能持续让会话保持活跃，所以不能说打开页面后一定在第 30 分钟自动退出。

## 6. 错误如何变成用户看得懂的提示

业务主动拒绝时抛出 `new Problem(400, "...")` 或 `Problem(409, "...")`。[ErrorMapper](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/ErrorMapper.java>) 将异常映射为 HTTP 状态和 `{"error":"..."}`。

前端 `api()` 检查 `response.ok`，不成功就抛出 JavaScript Error。编辑表单捕获后把消息写入 `edit-error`，表单保持打开。

数据库异常在当前版本被统一映射为 409，表达保守的冲突提示。这是简化：连接中断等也可能属于 PersistenceException，不能在分析日志时把所有这类异常都认定为业务冲突。

## 检查题

1. 把 `@PathParam` 改成 `@QueryParam` 会只是改个名字吗？
2. 删除按钮只在登录后显示，是否就完成了授权检查？
3. 401 和 409 在本项目各代表什么？

参考答案：不是，参数读取位置改变；不是，攻击者可以绕过页面直接请求，服务端必须过滤；401 是缺少有效身份验证，409 常见于版本冲突或数据库约束冲突。
