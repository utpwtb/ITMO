# SE.IFMO 相关问题

## 1. Java Servlet。实现特点、关键方法、与CGI和FastCGI相比的优缺点。

`javax.servlet` 和 `javax.servlet.http` 包提供了创建 Servlet 的接口和类。

**Servlet** 是一个 Java 类，通常继承自 `HttpServlet` 类并重写部分方法：

- `doGet` — 如果我们希望 Servlet 响应 GET 请求。
- `doPost` — 如果我们希望 Servlet 响应 POST 请求。
- `doPut`, `doDelete` — 如果我们希望 Servlet 响应 PUT 和 DELETE 请求（HTTP 中也有这些方法）。这些方法很少被实现，因为这些命令本身也很少见。
- `init`, `destroy` — 用于在 Servlet 创建和销毁时管理资源。

```java
public class NewServlet extends HttpServlet {
   
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    
        // 参数
        String parameter = request.getParameter("parameter");

        // 启动 HTTP 会话
        HttpSession session = request.getSession(true);
        session.setAttribute("parameter", parameter);

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();
        try {
            out.println("<html>");
            out.println("<head>");
            out.println("<title>标题</title>");
            out.println("</head>");
            out.println("<body>");
            out.println("<h1>Servlet 示例"+parameter+"</h1>");
            out.println("</body>");
            out.println("</html>");
        } finally {
            out.close();
        }
    } 

    @Override
    public String getServletInfo() {
        return "Servlet 示例";
    }

}
```

### Servlet vs CGI

- Servlet 在单个进程（具有附加功能的 HTTP 服务器，称为 Servlet 容器）中启动，并且只要该进程存在，它们就存在。
- CGI 每次都会创建一个新的进程实例来处理请求。这对性能是致命的。
- 由于每个请求都有一个新进程，这意味着 CGI 无法在内存中聚合多个请求的数据。

### Servlet vs FastCGI

- 使用 Servlet 时，Web 服务器可以直接调用应用程序。

## Servlet 容器。Servlet 的生命周期。

### Servlet 容器

**Servlet 容器** 是一个服务器程序，负责为 Servlet 提供系统支持，并根据规范中定义的规则管理其生命周期。

### 2. Servlet 的生命周期

Servlet 的生命周期包括以下步骤：

- 如果容器中不存在该 Servlet。

1. Servlet 类被容器加载。
2. 容器创建 Servlet 类的实例。
3. 容器调用 `init()` 方法。

- 处理客户端请求。每个请求都在自己独立的线程中处理。容器为每个请求调用 `service()` 方法。此方法确定传入请求的类型，并将其分发给处理该请求类型的相应方法。Servlet 开发人员必须提供这些方法的实现。如果收到了一个未实现其处理方法的请求，则会调用父类的方法，通常以向请求发起者返回错误而结束。
- 如果容器需要移除 Servlet，则调用 `destroy()` 方法，该方法将使 Servlet 停止服务。与 `init()` 方法类似，此方法在 Servlet 的整个生命周期中也只调用一次。

## 3. Servlet 中的请求分发。Servlet 过滤器。

### Servlet 中的请求分发

- Servlet 可以将请求处理委托给其他资源（Servlet、JSP 和 HTML 页面）。
- 分发通过 `javax.servlet.RequestDispatcher` 接口的实现来完成。
- 获取 `RequestDispatcher` 的两种方式 —— 通过 `ServletRequest`（绝对或相对 URL）和 `ServletContext`（仅绝对 URL）。
- 委托请求处理的两种方式 —— `forward` 和 `include`。

### Servlet 过滤器

Servlet 过滤器负责在请求到达 Servlet 之前对其进行预处理，和/或在 Servlet 发出响应之后对其进行后处理。

Servlet 过滤器可以：

- 在 Servlet 启动之前拦截其启动；
- 在 Servlet 启动之前确定请求内容；
- 修改包装传入请求的请求头和数据；
- 修改包装传出响应的响应头和數據；
- 在调用 Servlet 之后拦截其启动。

过滤器构建的基础是 `javax.servlet.Filter` 接口，它实现了三个方法：

`void init (FilterConfig config) throws ServletException;`

`void destroy ();`

`void doFilter (ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException;`

## 4. HTTP 会话 - 用途、Servlet 与会话的交互、传递会话标识符的方式。

会话是客户端和服务器之间建立的一段特定时间的连接，在此期间客户端可以向服务器发送任意数量的请求。会话直接在客户端和 Web 服务器之间建立。每个客户端都与服务器建立自己的会话。

要打开新会话，需使用 `HttpServletRequest` 接口的 `getSession()` 方法。该方法从传递给 Servlet 的请求中提取对应于该用户的 `HttpSession` 类的会话对象。

要将变量值保存在当前会话中，使用 `setAttribute()` 方法；读取使用 `getAttribute()` 方法；删除使用 `removeAttribute()` 方法。可以使用 `Enumeration getAttributeNames()` 方法获取当前会话中保存的所有变量名的列表。

### 传递会话标识符的方式

有 3 种跟踪会话的方式：

1. cookies
2. 重写 URL（对每个链接使用 `response.encodeURL()`，它会将会话标识符插入每个 URL 中。）
3. 表单隐藏字段

创建 cookies

```java
Cookie c = new Cookie (name, value);
public interface HttpSession {
    public void invalidate();
    ...
}
```

## 5. Servlet 上下文 - 用途、Servlet 与上下文交互的方式。

Servlet 上下文是一个 API，Servlet 可以通过它与容器交互。

Servlet 可以在不同时间获取其环境信息。在 Servlet 启动时，可以获取初始化信息；服务器信息在任何时候都可用，除此之外，任何请求都可能包含额外的特定信息。

服务器上下文信息可通过 `ServletConfig` 对象（该对象在初始化时传递给 Servlet）的 `getServletContext()` 方法获得。`init()` 方法应将私有引用保存在变量中。

`getAttribute ()`	通过名称/值属性对获取服务器信息的灵活方式。取决于服务器。

`GetMimeType ()`	返回给定文件的 MIME 类型。

`getRealPath ()`	此方法将相对路径或虚拟路径转换为相对于服务器 HTML 文档根目录的新路径。

`getServerInfo ()`	返回运行 Servlet 的网络服务的名称和版本。

`getServlet ()`	返回指定名称的 Servlet 对象。在访问其他 Servlet 的服务时很有用。

`getServletNames ()`	返回当前命名空间中可用的 Servlet 名称列表。

`log ()`	将信息写入 Servlet 日志文件。日志文件的名称和格式取决于服务器。

## 6. JavaServer Pages。特点、与 Servlet 相比的优缺点、应用领域。

JSP 是一种允许 Web 开发人员创建同时包含静态和动态组件的内容的技术，（并且允许将业务逻辑与表示层分离）

当加载到 Web 容器中时，JSP 页面由编译器（jasper）转换为 Servlet。

JavaServer Pages (JSP) 允许将页面的动态部分与静态 HTML 分开。动态部分包含在特殊的标签 "<% %>" 中：

```html
感谢您购买
<I><%= request.getParameter("title") %></I>
```

#### 优点：

● 高性能 — 被转换为 Servlet。
● 独立于平台 — 代码用 Java 编写。
● 允许使用 Java API。
● 易于理解 — 结构类似于普通 HTML。

#### 缺点：

● 如果应用程序完全基于 JSP，则难以调试。
● 在同时处理多个请求时可能发生冲突。

### JSP vs Servlet

JSP 允许用客户端语言（例如 HTML、CSS、JavaScript 等）编写模板文本，这些文本由 Java 代码片段支持。

JSP 还支持表达式语言，可用于访问基础数据（通过页面、请求、会话和应用程序中可用的属性）。

Servlet 在服务器上运行，拦截客户端发出的请求，并生成/发送响应。

## 7. JSP 的生命周期。

JSP 页面到 HTML 代码的转换由容器负责。

生命周期：

1. 转换 – JSP 容器检查 JSP 页面代码，解析它以创建 Servlet 代码。
2. 编译 – JSP 容器编译 jsp 类的源代码，并在此阶段创建类。
3. 类加载 – 容器在此阶段将类加载到内存中。
4. 实例化 – 调用已创建类的无参构造函数，以在内存中初始化类。
5. 初始化 – 在容器中调用 JSP 类对象的 `init` 方法，并使用部署描述符（web.xml）中指定的 `init` 参数初始化 Servlet 配置。
6. 请求处理 – 处理客户端对 JSP 页面请求的漫长生命周期。处理是多线程的，类似于 Servlet —— 为每个请求创建一个新线程，创建 `ServletRequest` 和 `ServletResponse` 对象，并调用 JSP 的服务方法。
7. 销毁 – JSP 生命周期的最后阶段，JSP 类从内存中移除。这通常发生在服务器关闭或应用程序卸载时。

方法：`jspInit() `, `_jspService()`, `jspDestroy()`

## 8. JSP 页面的结构。注释、指令、声明、脚本片段和表达式。

### 注释

在 JSP 页面中，注释可以分为两组：

- JSP 源代码注释
- HTML 标记注释。

JSP 源代码注释以特殊字符序列标记：`<%--` 在注释开头，`--%>` 在注释结尾。此类注释在 JSP 页面编译阶段被删除。

HTML 标记注释按照 HTML 语言的规则进行格式化。JSP 编译器将此类注释视为静态文本并将其放入输出的 HTML 文档中。HTML 注释内的 JSP 表达式会被执行。

```jsp
<%--
	将显示产品目录
	和客户的当前购物车。
--%>
```

```jsp
<!-- 页面创建日期: <%= new java.util.Date() %> -->
```

### 指令

JSP 页面可以向相应的容器发送消息，指示需要执行哪些操作。这些消息称为指令。所有指令都以 `<%@` 开头，后跟指令名称和属性及其值，并以 `%>` 结尾。JSP 页面中的指令导致容器请求执行特定服务，这些服务不会在生成的文档中声明。

```jsp
<%@ directive attribute1="value1" 
              attribute2="value2"
              ...
              attributeN="valueN" %>
```

### 声明

JSP 声明允许您定义变量、方法、内部类等。声明用于定义程序中使用的 Java 结构。

```jsp
<%! private int accessCount = 0; %>
自服务器启动以来页面访问次数: <%= ++accessCount %>
```

### 脚本片段

JSP 脚本片段允许将任何代码插入到处理页面时将创建的 Servlet 的方法中，允许使用大多数 Java 结构。

```jsp
<% 
String queryData = request.getQueryString();
out.println("附加请求数据: " + queryData); 
%>
```

### 表达式

JSP 表达式用于将 Java 值直接插入到输出中。Java 表达式被计算，转换为字符串并插入到页面中。

```jsp
当前时间: <%= new java.util.Date() %>
您的主机名: <%= request.getRemoteHost() %>
```

## 9. 在 JSP 中编写 Java 代码的规则。在脚本片段和表达式中可用的标准变量。

在 JSP 中编写 Java 代码的语法如下：

```jsp
<% 
  Java-code 
	   %>
```

在脚本片段和表达式中可用的标准变量：
`request`, `response`, `session`, `HttpSession`, `HttpServletRequest`, `HttpServletResponse`, `PrintWriter`

## 10. Bean 组件及其在 JSP 中的使用。

JavaBeans 是 Java 语言中按照特定规则编写的类。它们用于将多个对象组合成一个，以便于数据传输。

为了使类能够作为 bean 工作，它必须符合关于方法命名、构造函数和行为的某些约定。这些约定使得能够创建可以使用、替换和连接 JavaBeans 的工具。

描述规则：

- 类必须具有公共访问修饰符的无参构造函数。这样的构造函数允许工具创建对象而无需处理参数的额外复杂性。
- 类的属性必须可以通过 get、set 和其他方法（所谓的访问器方法）访问，这些方法必须遵循标准的命名约定。这使工具能够轻松自动识别和更新 bean 的内容。
- 类必须是可序列化的。这允许以独立于平台和虚拟机的方式可靠地保存、存储和恢复 bean 的状态。
- 类必须重写 `equals()`, `hashCode()` 和 `toString()` 方法。

### Bean 和 JSP

建立 JSP 与其对应的 bean 组件之间的关联

```jsp
<jsp:useBean id="_loginJSPBean" class="lbm.examples.LoginJSPBean" scope="session"/> 
```

传递表单所有字段的值

## 11. 标准 JSP 标签。在 JSP 中使用表达式语言 (EL)。

使用以下表达式引入 JSTL 标签库：

```jsp
// 用于创建循环、定义条件、在页面上输出信息等的主要标签。
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
// 用于处理 XML 文档的标签
<%@ taglib prefix="x" uri="http://java.sun.com/jsp/jstl/xml" %>
// 用于处理数据库的标签
<%@ taglib prefix="s" uri="http://java.sun.com/jsp/jstl/sql" %>
// 用于格式化和国际化信息（i10n 和 i18n）的标签
<%@ taglib prefix="f" uri="http://java.sun.com/jsp/jstl/fmt" %>
```

标准的 JSP 标签包括：
`<c:out>`, `<c:set>`, `<c:remove>`, `<c:if>`, `<c:choose>`, `<c:forEach>`, `<c:import>`, `<c:catch>`

表达式语言（简称 EL）提供了一种简洁的语法，用于在 jsp 页面中访问数组、集合、对象及其属性。它相当简单。插入以 $ 符号开头，然后将输出值括在花括号 {} 中：

```jsp
${attribute} 
${object.property}
```

## 12. Web 应用程序部署描述符中的 JSP 配置参数。

Java Web 应用程序使用部署描述符文件来定义哪些 URL 将传递给特定的 Servlet，哪些 URL 需要身份验证等。此部署描述符称为 web.xml，位于应用程序 WAR 文件的 WEB-INF/ 目录中。Web.xml 是 Web 应用程序 Servlet 标准的一部分。

## 13. 设计模式和架构模式。在 Web 应用程序中的使用。

主要架构模式：

- 多层架构
- 管道和过滤器
- 客户端-服务器
- 模型-视图-控制器
- 事件驱动架构
- 基于微服务的架构

主要设计模式：

- 简单工厂 (Simple Factory)；
- 工厂方法 (Factory Method)；
- 抽象工厂 (Abstract Factory)；
- 建造者 (Builder)；
- 原型 (Prototype)；
- 单例 (Singleton)。

## 14. Web 应用程序架构。MVC 模式。Model 1 和 Model 2 架构模型及其在 Java EE 平台上的实现。

**模型-视图-控制器** 是一种将应用程序数据、用户界面和控制逻辑分离为三个独立组件的方案：模型、视图和控制器——这样，每个组件的修改都可以独立进行。

- 模型 (Model) 提供数据及其处理方法：数据库查询、正确性检查（独立于视图（不知道如何可视化数据）和控制器（没有与用户的交互点））。
- 视图 (View) 负责从模型获取必要的数据并将其发送给用户（不处理用户输入的数据）。
- 控制器 (Controller) 提供用户和系统之间的“连接”。控制并将数据从用户导向系统，反之亦然。
  '
