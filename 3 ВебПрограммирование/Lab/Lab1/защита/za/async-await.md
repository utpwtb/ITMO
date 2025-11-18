# 🟢 一、中文部分：async / await 详解

### 1. 基本定义

**`async` / `await`** 是 JavaScript 中用于处理异步操作的  **语法糖（syntactic sugar）** 。

它的本质是基于  **Promise** ，但语法更像  **同步代码** ，让异步逻辑更直观、可读性更好。

> 简单说：
>
> * `async` 用来声明一个返回 **Promise** 的函数；
> * `await` 用来“等待”一个 Promise 的结果（暂停函数执行，直到 Promise 完成）。

---

### 2. 为什么需要 async / await

在没有它之前，我们写异步代码只能用：

* 回调函数（callback） → 容易变成 “回调地狱”
* Promise 链式调用（`.then().then().catch()`） → 虽然更好，但代码层级依然多

例如：

```js
getData()
  .then(data => process(data))
  .then(result => save(result))
  .catch(err => console.error(err));
```

`async/await` 可以让这段代码变成：

```js
async function run() {
  try {
    const data = await getData();
    const result = await process(data);
    await save(result);
    console.log("完成！");
  } catch (err) {
    console.error("出错：", err);
  }
}
```

是不是更像同步逻辑？而且清晰很多。

---

### 3. 基本语法规则

#### (1) `async` 函数：

```js
async function example() {
  return "Hello";
}
```

这相当于：

```js
function example() {
  return Promise.resolve("Hello");
}
```

也就是说， **任何 async 函数都会返回一个 Promise** 。

#### (2) `await` 表达式：

只能在 `async` 函数内部使用，用来等待 Promise 的结果：

```js
const result = await someAsyncFunction();
```

代码会在这里“暂停”，直到 `someAsyncFunction()` 的 Promise 完成，然后返回结果继续往下执行。

---

### 4. 完整示例

```js
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function start() {
  console.log("开始");
  await delay(1000);
  console.log("等待1秒后执行");
  await delay(1000);
  console.log("再等1秒后执行");
}
start();
```

输出：

```
开始
（1秒后）
等待1秒后执行
（再1秒后）
再等1秒后执行
```

这其实等价于 Promise 写法：

```js
delay(1000)
  .then(() => console.log("等待1秒后执行"))
  .then(() => delay(1000))
  .then(() => console.log("再等1秒后执行"));
```

---

### 5. 错误处理

`await` 会抛出 Promise 的错误，因此可以用 `try...catch` 捕获：

```js
async function fetchData() {
  try {
    const res = await fetch("https://api.example.com/data");
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.error("请求出错：", err);
  }
}
```

---

### 6. 并行执行（优化）

`await` 是**顺序执行**的。如果你希望多个异步操作 **并发执行** ：

```js
// ❌ 顺序等待：耗时更长
const data1 = await fetch(url1);
const data2 = await fetch(url2);
```

可以改为：

```js
// ✅ 并行执行
const [data1, data2] = await Promise.all([
  fetch(url1),
  fetch(url2)
]);
```

---

### 7. async/await 与 Promise 的关系

* `async` 函数返回的永远是一个  **Promise** ；
* `await` 实际上是语法糖，相当于对 `.then()` 的简化；
* 它让异步代码写起来像同步逻辑，但底层仍然是  **非阻塞的 Promise** 。

---

### 8. 常见错误

| 错误                      | 原因                       | 正确写法                      |
| ------------------------- | -------------------------- | ----------------------------- |
| `await`在普通函数中使用 | 只能在 `async`函数中使用 | 把函数改成 `async function` |
| 忘记 try/catch            | 异常无法捕获               | 使用 `try...catch`          |
| 顺序等待而非并行          | 效率低                     | 用 `Promise.all()`并行处理  |

---

### ✅ 小结（中文）

| 关键词    | 含义                                 |
| --------- | ------------------------------------ |
| `async` | 声明一个返回 Promise 的异步函数      |
| `await` | 等待 Promise 完成并返回结果          |
| 优点      | 代码更简洁、可读性强、异常处理更自然 |
| 缺点      | 不能直接用于顶层（需包装函数）       |
| 本质      | Promise 的语法糖                     |

---

## 🟣 二、Русская часть：async / await подробно

### 1. Определение

**`async` / `await`** — это современный способ работы с асинхронным кодом в JavaScript.

Это **синтаксический сахар** над `Promise`, который делает код  **читаемым как синхронный** .

> `async` объявляет функцию, которая всегда возвращает Promise.
>
> `await` приостанавливает выполнение, пока Promise не завершится.

---

### 2. Зачем нужно

Раньше асинхронный код выглядел так:

```js
getData()
  .then(process)
  .then(save)
  .catch(console.error);
```

С `async/await` он становится простым и линейным:

```js
async function run() {
  try {
    const data = await getData();
    const result = await process(data);
    await save(result);
  } catch (err) {
    console.error(err);
  }
}
```

---

### 3. Основные правила

* `async` перед функцией → она возвращает Promise;
* `await` можно использовать  **только внутри async-функции** ;
* `await` «ждёт» Promise, не блокируя остальной код.

---

### 4. Пример

```js
function delay(ms) {
  return new Promise(res => setTimeout(res, ms));
}

async function demo() {
  console.log("Начало");
  await delay(1000);
  console.log("Прошла 1 секунда");
  await delay(1000);
  console.log("Прошла ещё 1 секунда");
}

demo();
```

---

### 5. Обработка ошибок

```js
async function fetchData() {
  try {
    const res = await fetch("https://api.example.com");
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.error("Ошибка запроса:", err);
  }
}
```

---

### 6. Параллельное выполнение

Если нужно ждать несколько операций одновременно:

```js
const [user, posts] = await Promise.all([
  fetch("/user"),
  fetch("/posts")
]);
```

Так код выполняется  **быстрее** , чем последовательное ожидание.

---

### 7. Итог

| Ключ                 | Значение                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| `async`                | возвращает Promise                                                                             |
| `await`                | ждёт Promise                                                                                         |
| Преимущества | читаемость, простота, централизованная обработка ошибок |
| Основа             | Promises                                                                                                 |
| Важно               | Не использовать `await`вне `async`функции                                    |

---

✅ **简短总结 / Краткий вывод：**

> `async/await` = **写起来像同步，运行时仍异步。**
>
> 它是 Promise 的优雅封装，使异步编程更接近同步逻辑，更易维护。
