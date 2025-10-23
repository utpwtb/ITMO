**URL 和 URN 都是 URI 的子集**。

* **URI (统一资源标识符)**：是一个人的**身份证号码**。它的唯一作用是**标识**这个人，确保不会和其他人混淆。
* **URL (统一资源定位符)**：是这个人的**家庭住址**。它不仅标识了这个人，还明确指出了**如何找到**他（通过这个地址）。
* **URN (统一资源名称符)**：是一个**永久的、与位置无关的身份证号**（比如一个全球唯一的UUID）。无论这个人搬到世界何处，这个号码永远不变，只负责标识，但不提供位置信息。

### 1. URI - 统一资源标识符 (Uniform Resource Identifier)

**定义**：URI 是一个最宽泛的概念，指的是用于**标识**某一互联网资源字符串。这种标识可以是资源的**名称**、**位置**，或者两者兼有。

**核心作用**：**标识**（Identity）。只要是用来唯一标识一个资源的，就是 URI。

**范围**：**URI 包含了 URL 和 URN**。所有 URL 和 URN 都是 URI，但并非所有 URI 都是 URL 或 URN（理论上存在既是 URL 又是 URN 的 URI，但实践中极少）。

**例子**：

* `https://www.example.com/index.html` (这是一个 URL，同时也是 URI)
* `urn:isbn:0451450523` (这是一个 URN，同时也是 URI)
* `mailto:help@example.com` (这是一个 URI，但它既不是典型的 URL也不是 URN)

### 2. URL - 统一资源定位符 (Uniform Resource Locator)

**定义**：URL 是 URI 中最常见的一种。它不仅标识了资源，更重要的是提供了**访问该资源的方法**和**位置**。它通常包含协议、主机名、路径、端口等组成部分。

**核心作用**：**定位**（Location）。它告诉你资源在哪里以及如何获取它。

**组成部分**（以 `https://www.example.com:443/products/index.html?key=value#section` 为例）：

* **`https://`**：协议（Scheme），表示使用何种协议访问资源（HTTP, HTTPS, FTP等）。
* **`www.example.com`**：主机名（Host），资源所在服务器的地址。
* **`:443`**：端口（Port），可选，服务器上服务的入口（HTTPS默认443，通常省略）。
* **`/products/index.html`**：路径（Path），资源在服务器上的具体位置。
* **`?key=value`**：查询字符串（Query String），可选，提供给服务器的参数。
* **`#section`**：片段（Fragment），可选，通常指向资源内部的某个锚点。

**例子**：

* 网页地址：`https://www.google.com/`
* 文件地址：`ftp://example.com/files/document.pdf`
* 图片地址：`https://example.com/images/photo.jpg`

**特点**：**URL 依赖于位置**。如果资源被移动了，原来的 URL 就会失效（出现 404 错误）。

### 3. URN - 统一资源名称符 (Uniform Resource Name)

**定义**：URN 是 URI 的另一种形式，它的目的是为资源提供一个**全局唯一、持久不变的名称**，而不管资源的具体位置在哪里。

**核心作用**：**命名**（Name）。它只关心“这个资源叫什么”，而不关心“这个资源在哪里”和“如何获取它”。

**格式**：所有 URN 都以 `urn:` 开头，后面跟着命名空间标识符和具体的名称。

* `urn:<namespace>:<namespace-specific-string>`

**例子**：

* **图书ISBN号**：`urn:isbn:0451450523`
  * 这唯一标识了《银河系漫游指南》这本书，但并没有告诉你从哪里能下载或买到它。
* **UUID**：`urn:uuid:6e8bc430-9c3a-11d9-9669-0800200c9a66`
* **IETF标准文档**：`urn:ietf:rfc:7230` (标识 RFC 7230 文档)

**特点**：**URN 是持久且与位置无关的**。理想情况下，一个 URN 一旦被分配就永远不会改变。要访问 URN 标识的资源，需要一个解析系统将它映射到一个当前的 URL。**然而，这种全球性的解析系统并未被广泛实现和应用**，因此 URN 在实践中远没有 URL 常见。

### 总结与对比表格

| 特性                   | URI (统一资源标识符)                         | URL (统一资源定位符)                     | URN (统一资源名称符)         |
| :--------------------- | :------------------------------------------- | :--------------------------------------- | :--------------------------- |
| **目的**         | **标识**资源                           | **定位**资源                       | **命名**资源           |
| **核心问题**     | “它是什么？”                               | “它在哪里？怎么获取？”                 | “它叫什么？”               |
| **是否包含位置** | 可能包含，也可能不包含                       | **是**                             | **否**                 |
| **是否依赖位置** | -                                            | **是**（资源移动，URL失效）        | **否**（名称永久不变） |
| **范围**         | **超集**，包含所有 URL 和 URN          | **URI 的子集**                     | **URI 的子集**         |
| **常见例子**     | `https://...`, `mailto:...`, `urn:...` | `https://www.example.com`              | `urn:isbn:0451450523`      |
| **前缀**         | 多种多样                                     | `http://`, `ftp://`, `https://` 等 | 必须以 `urn:` 开头         |

### 结论

* 当你需要在网络上**找到并访问**一个资源（如打开网页、下载文件）时，你使用的是 **URL**。它是 URI 的实现者，是互联网的基石。
* 当你只想给一个资源一个**永久不变的名字**，而不关心它当前存放在哪里时，你理想中使用的是 **URN**。它是一个美好的概念，但实践应用有限。
* **URI** 是一个总称，涵盖了所有用于标识资源的字符串。在大多数日常对话中，当人们说“网址”时，他们指的其实是 URL，但技术上更准确的术语是 URI。

简单记法：**所有的 URL 都是 URI，所有的 URN 也是 URI，但并非所有的 URI 都是 URL**。

---



# REST（表述性状态转移）

## 软件工程中的Web技术

- *Representational State Transfer*（表述性状态转移）—— 一种网络协议架构风格，用于提供对信息资源的访问。
- 核心概念：

  - 数据应以少量标准格式（HTML、XML、JSON）进行传输
  - 网络协议应支持缓存，不应依赖于网络层，且不应在"请求-响应"对之间保持状态信息
- REST的对立面是基于远程过程调用（*Remote Procedure Call — RPC*）的方法

### 什么是REST？

REST（表述性状态转移）是一种软件架构风格，由Roy Fielding于2000年在其博士论文中提出。它定义了一组约束和原则，用于创建可扩展、可靠和高效的Web服务。

### 核心特性详解：

1. **标准数据格式**

   - REST要求数据通过标准化的格式传输，最常用的是：
     - **HTML**：超文本标记语言，用于网页
     - **XML**：可扩展标记语言，结构化数据格式
     - **JSON**：轻量级的数据交换格式，目前最流行
2. **无状态性**

   - 每个请求必须包含处理该请求所需的所有信息
   - 服务器不会在请求之间保存客户端的状态信息
   - 优点：提高可扩展性，简化服务器设计
3. **缓存支持**

   - RESTful架构明确支持缓存机制
   - 可以减少客户端-服务器交互，提高性能
4. **分层系统**

   - 客户端不需要了解是否直接连接到最终服务器还是中间层
   - 提高了系统的可扩展性和安全性

### REST vs RPC

| 特性               | REST               | RPC            |
| ------------------ | ------------------ | -------------- |
| **设计理念** | 资源导向           | 动作导向       |
| **通信方式** | 通过标准HTTP方法   | 自定义方法调用 |
| **状态管理** | 无状态             | 可能保持状态   |
| **数据格式** | 标准格式(JSON/XML) | 任意格式       |
| **可缓存性** | 天然支持           | 有限支持       |

### 实际应用

现代Web API（如Twitter、Google等提供的API）大多采用RESTful设计，使用：

- HTTP方法：GET（获取）、POST（创建）、PUT（更新）、DELETE（删除）
- 标准状态码：200（成功）、404（未找到）、500（服务器错误）等
- JSON作为主要数据交换格式

---



# HTTP 方法

OPTIONS — 用于获取服务器支持的功能
GET — 请求获取指定资源的内容
HEAD — 类似于GET请求，但响应中不包含消息体
POST — 向指定资源提交数据
PUT — 将请求的内容上传到指定的URI位置

### HTTP方法概述

HTTP方法（有时也称为HTTP动词）表明确客户端希望对目标资源执行什么操作。它们是RESTful架构的核心组成部分。

### 各方法详解：

#### 1. OPTIONS

- **功能**：用于获取目标资源支持的通信选项信息
- **特点**：

  - 返回服务器支持的HTTP方法列表
  - 常用于CORS（跨域资源共享）预检请求
- **示例**：

  ```http
  OPTIONS /api/users HTTP/1.1
  Host: example.com
  ```

  **响应**：
  ```http
  HTTP/1.1 200 OK
  Allow: GET, POST, HEAD, OPTIONS
  ```

#### 2. GET

- **功能**：请求获取指定资源
- **特点**：
  - 应该是安全且幂等的（多次请求产生相同结果）
  - 参数通过URL传递（查询字符串）
  - 可被缓存
- **示例**：
  ```http
  GET /api/users/123 HTTP/1.1
  Host: example.com
  ```

#### 3. HEAD

- **功能**：与GET相同，但服务器只返回头部信息，不返回消息体
- **用途**：
  - 检查资源是否存在
  - 查看资源是否被修改（通过Last-Modified头）
  - 获取资源元数据而不下载内容
- **示例**：
  ```http
  HEAD /large-file.pdf HTTP/1.1
  Host: example.com
  ```

#### 4. POST

- **功能**：向指定资源提交数据
- **特点**：
  - 非幂等（多次提交可能产生不同结果）
  - 数据通过请求体传输
  - 通常用于创建新资源
- **示例**：
  ```http
  POST /api/users HTTP/1.1
  Host: example.com
  Content-Type: application/json

  {"name": "John", "email": "john@example.com"}
  ```

#### 5. PUT

- **功能**：替换指定资源的全部内容
- **特点**：
  - 幂等（多次相同请求产生相同结果）
  - 用于更新或创建资源
  - 客户端提供完整的资源表示
- **示例**：
  ```http
  PUT /api/users/123 HTTP/1.1
  Host: example.com
  Content-Type: application/json

  {"id": 123, "name": "John Updated", "email": "john@example.com"}
  ```

### 其他重要HTTP方法

#### PATCH

- **功能**：对资源进行部分修改
- **与PUT的区别**：PUT替换整个资源，PATCH只更新指定字段

#### DELETE

- **功能**：删除指定资源
- **特点**：幂等方法

#### TRACE

- **功能**：用于诊断，返回接收到的请求内容

### 安全性与幂等性

| 方法              | 安全 | 幂等 |
| ----------------- | ---- | ---- |
| **GET**     | ✅   | ✅   |
| **HEAD**    | ✅   | ✅   |
| **OPTIONS** | ✅   | ✅   |
| **POST**    | ❌   | ❌   |
| **PUT**     | ❌   | ✅   |
| **DELETE**  | ❌   | ✅   |
| **PATCH**   | ❌   | ❌   |

- **安全**：不应修改服务器状态的方法
- **幂等**：多次执行相同操作产生相同结果

### 实际应用建议

1. **正确使用方法语义**：GET用于读取，POST用于创建，PUT用于全量更新等
2. **遵守RESTful原则**：使API设计更加直观和一致
3. **考虑安全性**：敏感操作使用POST而非GET
4. **利用缓存**：对GET请求合理设置缓存头

---



# HTTP 头部

**软件工程中的Web技术**

- 格式：键:值
- 4个分组：
  - 通用头部(General Headers) — 可包含在客户端和服务端的任何消息中。示例 — Cache-Control。
  - 请求头部(Request Headers) — 仅用于客户端请求。示例 — Referer。
  - 响应头部(Response Headers) — 仅用于服务端响应。示例 — Allow。
  - 实体头部(Entity Headers) — 伴随任何消息实体。示例 — Content-Language。

### HTTP头部概述

HTTP头部是HTTP协议的重要组成部分，它们以键值对的形式在客户端和服务器之间传递元数据信息，用于控制通信行为、描述消息内容以及传递其他相关信息。

### 四大头部类型详解：

#### 1. 通用头部 (General Headers)

- **作用**：适用于请求和响应消息的通用头部字段
- **特点**：与消息体内容无关，提供关于整个消息的基本信息
- **常见示例**：
  - `Cache-Control`: 控制缓存行为（如 `max-age=3600`）
  - `Connection`: 控制网络连接（如 `keep-alive`）
  - `Date`: 消息创建的时间戳
  - `Transfer-Encoding`: 指定传输编码方式（如 `chunked`）

#### 2. 请求头部 (Request Headers)

- **作用**：客户端向服务器发送请求时提供的附加信息
- **特点**：仅出现在请求消息中，描述客户端信息和请求偏好
- **常见示例**：
  - `Referer`: 表示请求来源的URL
  - `User-Agent`: 客户端软件信息（浏览器、操作系统等）
  - `Accept`: 客户端可接受的内容类型（如 `application/json`）
  - `Authorization`: 身份验证凭证（如Bearer token）

#### 3. 响应头部 (Response Headers)

- **作用**：服务器响应时提供的附加信息
- **特点**：仅出现在响应消息中，描述服务器信息和响应状态
- **常见示例**：
  - `Allow`: 指定资源支持的HTTP方法（如 `GET, POST`）
  - `Server`: 服务器软件信息
  - `Set-Cookie`: 设置客户端的Cookie
  - `Location`: 重定向目标URL（用于3xx响应）

#### 4. 实体头部 (Entity Headers)

- **作用**：描述消息体内容的元数据
- **特点**：适用于包含消息体的请求和响应
- **常见示例**：
  - `Content-Language`: 内容使用的语言（如 `zh-CN`）
  - `Content-Type`: 媒体类型（如 `text/html; charset=utf-8`）
  - `Content-Length`: 消息体大小（字节数）
  - `Content-Encoding`: 内容编码方式（如 `gzip`）

### 实际应用示例

**HTTP请求示例：**

```http
GET /api/data HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: application/json
Authorization: Bearer token123
```

**HTTP响应示例：**

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 128
Cache-Control: max-age=3600
Server: nginx/1.18.0
```

### 重要性和最佳实践

1. **性能优化**：合理使用缓存头部(`Cache-Control`, `ETag`)提升性能
2. **安全增强**：通过安全头部(`Content-Security-Policy`, `X-Frame-Options`)加强安全
3. **内容协商**：使用 `Accept`系列头部实现多格式支持
4. **状态管理**：通过 `Set-Cookie`和 `Cookie`头部维护会话状态
5. **编码处理**：正确设置 `Content-Encoding`和 `Transfer-Encoding`确保数据传输

---
