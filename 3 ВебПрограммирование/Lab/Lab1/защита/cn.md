# 🌐 来自 se.ifmo 的问题

## 1. HTTP 协议

**请求与响应的结构、请求方法、服务器响应代码、请求与响应头**

 **HTTP** （HyperText Transfer Protocol，超文本传输协议）是一种 **应用层数据传输协议** 。最初用于传输超文本文档（HTML 格式），如今用于传输任意类型的数据。

HTTP 基于 **“客户端–服务器”** 模型，即假定存在以下两类实体：

* **客户端（client）** — 发起连接并发送请求；
* **服务器（server）** — 等待连接、接收请求、执行操作并返回响应结果。

### 🔹 HTTP 请求结构

一个 HTTP 请求由以下几部分组成（顺序固定）：

1. **请求行（Request Line）**
2. **消息头（Message Headers）**
3. **空行（分隔符）**
4. **消息体（Entity Body）** （可选）

请求行指明：

* 请求方法；
* 请求的 URL 地址；
* 使用的 HTTP 协议版本。

消息头包含：

* 请求/响应的元信息；
* 参数与内容说明；
* 其他辅助信息。

消息体包含请求要传输的数据（可选）。

### 🔹 常见请求方法

* `GET`：请求资源，只用于获取数据；
* `HEAD`：类似 GET，但不返回响应体；
* `POST`：向指定资源发送数据（例如表单提交）；
* `PUT`：创建或替换资源；
* `DELETE`：删除资源；
* `CONNECT`：建立到服务器的“隧道”；
* `OPTIONS`：获取服务器支持的方法；
* `TRACE`：回显请求（用于调试）；
* `PATCH`：部分更新资源。

### 🔹 响应状态码

1. **1xx** — 信息（Informational）
2. **2xx** — 成功（Success）
3. **3xx** — 重定向（Redirection）
4. **4xx** — 客户端错误（Client Error）
5. **5xx** — 服务器错误（Server Error）

---

## 2. HTML 标记语言

**特点、主要标签与属性**

HTML 文档由**元素（element）**组成。元素以**标签（tag）**表示起始与结束。

某些标签 **没有内容** ，不需要关闭，例如：

```html
<!-- 错误写法 -->
<input type="text"></input>
<!-- 正确写法 -->
<input type="text">
```

HTML5 引入了 **语义化标签** ：

* `<header>`
* `<footer>`
* `<section>`

它们与 `<div>` 类似，但表达了更明确的文档结构含义。

---

## 3. HTML 页面结构与文档对象模型（DOM）

**DOM（Document Object Model）** 是 HTML 与 XML 文档的编程接口。它以对象的形式描述文档结构，使程序可以访问和修改文档内容。

（换句话说，DOM 连接了网页与脚本语言。）

通过 DOM 可以：

* 创建、添加节点；
* 获取节点；
* 修改节点；
* 改变节点间的关系；
* 删除节点。

访问 DOM 通常通过全局对象 `document` 或 `window` 实现。

此外还有 **BOM（Browser Object Model）** —— 浏览器对象模型，用于操作浏览器窗口、对话框、监视器信息等。

---

## 4. HTML 表单

**HTTP 方法、放置规则与输入字段类型**

表单用于用户与服务器之间的数据交互。

由 `<form>` 标签定义，可包含以下属性：

* `action`：处理表单的 URI（必填）；
* `method`：HTTP 方法（默认 `GET`）；
* `enctype`：编码类型；
* `accept`：允许上传的 MIME 类型；
* `name`：表单名称；
* `onsubmit` / `onreset`：事件处理函数；
* `accept-charset`：字符编码。

### 常见输入类型：

* `<input>`：按钮、文本、密码等；
  * 类型包括 `submit`, `reset`, `button`, `image`；
* `checkbox`：复选框；
* `radio`：单选框；
* `select`：下拉选择；
* `textarea`：多行文本；
* `password`：密码输入；
* `hidden`：隐藏字段；
* `file`：文件上传。

---

## 5. CSS（层叠样式表）

**规则结构、选择器类型、优先级、相对 HTML 内联样式的优势**

**CSS** 是一种描述文档外观的语言。

### 🔹 CSS 规则

由两个部分组成：

1. **选择器（selector）** ；
2. **声明块（declaration block）** 。

### 🔹 选择器类型

* `*` — 任意元素；
* `div` — 指定标签；
* `#id` — 按 ID；
* `.class` — 按类名；
* `[name="value"]` — 按属性；
* `:visited`, `:hover` — 伪类；
* `div p` — 后代选择器；
* `div > p` — 直接子代；
* `div ~ p` — 同级后续兄弟；
* `div + p` — 紧邻兄弟。

### 🔹 优先级规则

1. 行内样式（`style`）；
2. 含有 `id` 的选择器；
3. 类、伪类、属性；
4. 标签与伪元素。

可使用 `!important` 提高样式优先级。

---

## 6. LESS、Sass、SCSS

**主要特性、区别、兼容性与转译机制**

### 🔸 LESS

LESS 是 CSS 的超集，所有 CSS 代码都兼容。

**优势：**

* 支持变量与作用域；
* 支持运算与颜色混合；
* 支持嵌套；
* 支持参数组合。

通过引入 `less.js` 实现实时编译：

```html
<script src="less.js"></script>
<link rel="stylesheet/less" href="style.less">
```

### 🔸 Sass

Sass 是基于 CSS 的元语言，提高代码抽象层次。

**优势：**

* 嵌套规则；
* 变量；
* mixin（可复用规则组）；
* 继承 `@extend`；
* 逻辑控制（if / for）。

但  **Sass 不能直接在浏览器中编译** ，需先转为 CSS。

### 🔸 SCSS

Sass 的另一种语法，更接近 CSS。

**特性：**

* `@import` 支持；
* 嵌套；
* `$变量`；
* 运算；
* 字符串拼接：`#{$var}`。

---

## 7. 客户端脚本与 JavaScript

脚本嵌入网页中，通过 `<script>` 标签引入。

JavaScript 是一种**面向对象**的语言，支持：

* 动态类型；
* 自动垃圾回收；
* 闭包；
* 函数式特性（函数是一等对象）。

**数据类型：**

* `number`
* `string`
* `boolean`
* `null`
* `undefined`
* `object`

---

## 8. ECMAScript 与 ES6 / ES7 特性

**ECMAScript** 是 JavaScript 的标准规范。

### 🔹 ES6 新增内容

* 类与模块；
* `for/of` 循环；
* 生成器（generator）；
* Promise；
* let / const；
* 箭头函数；
* 模板字符串；
* 解构赋值；
* Set / Map 集合；
* Proxy 与 Reflect。

### 🔹 ES7 新增内容

* 指数运算符 `**`
* `Array.prototype.includes()`

---

## 9. 同步与异步 HTTP 请求，AJAX

* **同步请求** ：脚本等待服务器响应；
* **异步请求** ：脚本继续执行，不阻塞。

```js
var request = getXmlHttpRequest();
request.onreadystatechange = function() {
  if (request.readyState == 4) {
    // 数据已返回
  }
};
request.open('GET', url, true);
request.send(null);
```

**AJAX（Asynchronous JavaScript and XML）**

通过异步通信更新页面局部内容，无需刷新整页。

---

## 10. jQuery 库

**jQuery** 是简化 DOM 操作与 AJAX 的 JavaScript 库。

```html
<script src="jquery-2.2.2.min.js"></script>
```

示例：

```js
$("div.test").add("p.quote").addClass("blue").slideDown("slow");
```

AJAX 示例：

```js
$.ajax({
  type: "POST",
  url: "some.php",
  data: {name: 'John', location: 'Boston'},
  success: function(msg){
    alert("Data Saved: " + msg);
  }
});
```

---

## 11. 使用 SuperAgent 实现 AJAX

```js
request
  .post('/api/pet')
  .send({ name: 'Manny', species: 'cat' })
  .set('X-API-Key', 'foobar')
  .set('Accept', 'application/json')
  .end(function(err, res){
    if (err || !res.ok) alert('Error');
    else alert('Got: ' + JSON.stringify(res.body));
  });
```

---

## 12. CGI 脚本

**定义、用途与特点**

CGI（Common Gateway Interface）是 Web 服务器与外部程序交互的标准接口。

每个请求由单独的 CGI 进程处理，通过 `stdin` / `stdout` 进行通信。

---

## 13. FastCGI 与 CGI 区别

CGI 每个请求都新建进程，效率低。

**FastCGI** 保持进程持久化，可处理多个请求，性能高。

PHP 通过 `pthreads` 实现多线程，但仅限 CLI 模式。

---

## 14. PHP

**语法、类型、在网页中的嵌入、HTTP 请求处理与 OOP 特性**

PHP 是常用于 Web 开发的脚本语言。

### 🔹 数据类型

* 标量：`int`, `float`, `bool`, `string`
* 复合：`array`, `object`
* 其他：`resource`, `null`
* 伪类型：`mixed`, `callback`, `void`

### 🔹 HTTP 请求示例

```php
$url = 'https://translate.yandex.ru';
$context = stream_context_create([
  'http' => [
    'method' => 'POST',
    'content' => http_build_query([
      'lang' => 'ru-en',
      'text' => 'Все получилось',
    ])
  ]
]);
```

### 🔹 面向对象

```php
class ClassName {
  public $publicName;
  private $privateName;
  protected $protectedName;
  
  const CONST_VAL = 'val';

  public function getPrivateName() {
    return $this->privateName;
  }
}
```

PHP 支持：

* 封装；
* 继承（`extends`）；
* 多接口（`implements`）；
* trait；
* 构造/析构：`__construct()`, `__destruct()`；
* 魔术方法：`__get()`, `__set()`, `__clone()`。

---

# 🎓 保护性问题（附加题）

## 1. CORS

跨域资源共享（Cross-Origin Resource Sharing）允许浏览器从其他域请求资源。

关键头部：

* `Origin`
* `Access-Control-Allow-Origin`
* `Access-Control-Allow-Methods`
* `Access-Control-Allow-Credentials`

---

## 2. HTTPS

HTTPS 通过加密通信防止数据泄漏与中间人攻击。

服务器需提供由可信机构签发的证书以证明身份。

---

## 3. JavaScript 中的 OOP

JS 采用**原型继承**机制。

```js
function Person(name) {
  this.name = name;
  this.greeting = function() {
    alert("Hi! I'm " + this.name);
  };
}
Person.prototype.fun = function() { ... }
```

### 🔹 this

`this` 取决于函数的调用方式，可通过 `bind()` 修改。

### 🔹 ES6 类语法

```js
class Foo {
  constructor(a, b) {
    this.value = a + b;
  }
}
class Bar extends Foo {
  constructor() {
    super();
  }
}
```

---

## 4. CSS 动画

### Transition（过渡）

控制属性变化的平滑过渡：

* `transition-property`
* `transition-duration`
* `transition-timing-function`
* `transition-delay`
* `transitionend`（事件）

### Animation（动画）

使用 `@keyframes` 定义关键帧序列，结合 `animation` 属性使用。

---

## 5. CSS 继承性

**可继承属性：**

`color`, `font`, `cursor`, `list-style`, `letter-spacing`, `line-height`, `text-indent`, `text-transform` 等。

 **不可继承属性** ：如 `margin`, `padding`, `border` 等。

特殊关键字：

* `inherit` — 强制继承；
* `initial` — 还原为默认值。

---

## 6. Web 服务器与应用服务器

* **Web 服务器** ：处理 HTTP 请求并返回静态或动态资源（HTML、图片等）。
* **应用服务器** ：执行业务逻辑代码（动态页面、API 服务）。

---

## 7. HTTP 请求示例

### x-www-form-urlencoded

```http
POST / HTTP/1.1
Host: foo.com
Content-Type: application/x-www-form-urlencoded

say=Hi&to=Mom
```

### multipart/form-data

```http
POST /test.html HTTP/1.1
Host: example.org
Content-Type: multipart/form-data; boundary="boundary"

--boundary
Content-Disposition: form-data; name="field1"

value1
--boundary
Content-Disposition: form-data; name="field2"; filename="example.txt"

value2
```

---

## 8. Cookie

Cookie 是浏览器保存的小数据片段，用于：

* 会话管理；
* 个性化；
* 用户追踪。

### 创建方式

服务器响应头中包含：

```
Set-Cookie: name=value; Path=/; Expires=...
```

浏览器后续请求会自动携带：

```
Cookie: name=value
```
