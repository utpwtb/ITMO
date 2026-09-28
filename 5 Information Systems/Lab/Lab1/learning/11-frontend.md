# 11 原生 JavaScript 前端怎样连接后端

源码：[index.html](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/webapp/index.html>)、[app.js](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/webapp/app.js>)、[style.css](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/webapp/style.css>)。

## 1. 本项目没有引入前端框架

页面使用浏览器原生 DOM API、事件、fetch 和 dialog。它不是 React/Vue 项目，也不是通过服务器模板每次渲染整张电影表。

HTML 放好页面容器；JavaScript 请求 JSON 后创建表格行和输入框；CSS 决定这些元素怎样排列。分清这三者，就能知道该去哪里修改功能。

## 2. DOM 和选择器

DOM 是浏览器中页面元素组成的对象树。项目定义：

```javascript
const $ = id => document.getElementById(id);
```

这里 `$` 是自己起的函数名，不是 jQuery。`$('rows')` 表示找到 HTML 中 `id="rows"` 的元素。

代码常用 `document.createElement()` 创建节点，`append()` 插入节点，`replaceChildren()` 替换子节点，`textContent` 设置纯文本。将电影名字写入 textContent 不会把其中的 HTML 字符串当作标签执行，这是显示用户输入时有价值的习惯。

## 3. state 是页面自己的记忆

| 字段 | 当前用途 |
|---|---|
| `kind` | 当前菜单栏目 |
| `page`、`size`、`total` | 分页状态 |
| `revision` | 浏览器上次观察到的版本 |
| `csrf` | 当前会话的修改请求 token |
| `editing` | 当前编辑对象的类型、ID、旧 version |
| `detail` | 当前打开的详情对象 |
| `busy` | 避免定时轮询自身重叠 |

state 不等于数据库。页面刷新后它会重新建立；真实电影数据在服务器中。并且这里的 busy 只用于轮询流程，不是整个前端所有异步操作的全局互斥锁。

## 4. api() 封装了哪些重复逻辑

教学节选：

```javascript
const response = await fetch('api/' + path, {
  method,
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': state.csrf
  },
  body: body === undefined ? undefined : JSON.stringify(body)
});
```

`fetch` 返回 Promise；`await` 等待它完成并继续后面的逻辑，不代表把整个浏览器线程锁死。响应仍需读取、解析，HTTP 400/500 也需要主动检查 `response.ok`，不能只依靠网络异常捕获。

项目统一把接口错误变成 JavaScript Error，然后由不同界面的调用者决定显示位置。登录错误显示在登录区，编辑错误显示在弹窗，连接问题显示为通知。

## 5. 一个 schema 生成四种表单

这里的前端 `schemas` 是**表单元数据**，不是 PostgreSQL 的 schema。

一个字段配置包含：字段名、俄语标签、控件类型、是否必填、枚举或关联集合，以及数值范围。`edit(kind,id)` 遍历配置生成控件。

| type | 创建什么 |
|---|---|
| text | 普通输入框 |
| integer / number | 数值输入框 |
| enum | 枚举下拉框 |
| ref | 已存在对象的下拉框 |
| long | 保留文本精度的整数输入框 |

为什么 long 不直接转 `Number`？因为过大的整数可能在浏览器中被舍入，服务器再正确解析也救不回已经丢失的数字。当前表单输入字符串直接交给后端转换。

## 6. ref 类型怎样复用对象

电影编辑窗先请求坐标/人员列表，选项中显示对象 ID 和名字，但真正的 value 是 ID。这样用户选择导演时提交的是对既有记录的引用。

创建和编辑共用一套弹窗：有 ID 就先读取对象并填入旧值，没有 ID 就展示新建表单。旧 version 也保存在 editing 中，用户不直接编辑它。

## 7. null 与空字符串在表单里的转换

可空字段留空时，提交 null；必填但允许空字符串的字段（例如 tagline）留空时仍提交字符串 `""`。

这是前端对题目约束做的细分，不是所有带星号字段都必须至少一个字符。最终是否合法仍由服务器决定。

## 8. 页面导航不需要重新加载整个网站

菜单点击后，`navigate()` 修改 kind，隐藏或显示对应 section，再调用 refresh。电影列表向服务器请求一页数据；辅助对象则读取整个列表后在页面截取一页。

`details()` 读取指定 ID，`renderObject()` 递归展示关联对象字段。当前服务端 JSON 对 null 字段可能省略，详情不应被误认为一定显示每个空字段；主表则按固定字段列展示占位。

## 9. 并发交互仍有可以改进的地方

当前方案足够表达实验功能，但不是完善的前端状态框架。快速切换筛选与翻页时，多个请求可能交错返回；更复杂的界面可以使用请求编号或 AbortController 丢弃旧结果。当前全局集合变化也会让不相关的编辑窗收到提示，真正是否冲突仍由对象 version 决定。

这些是读代码后应认识的边界，不表示本教程已修改了应用。

## 动手观察

打开浏览器开发者工具的 Network 标签，再依次登录、打开列表、翻页、保存电影。观察请求方法、URL、Request Payload、Response 和状态码；不要只看按钮是否消失。

## 检查题

1. 本项目的 `$()` 来自哪个库？
2. HTTP 400 一定会让 fetch 自己抛异常吗？
3. 为什么前端枚举下拉框之外，服务器仍要校验枚举？

参考答案：没有库，是自定义函数；不会，需要检查状态；请求可以绕过页面，而且前端版本可能落后于后端规则。
