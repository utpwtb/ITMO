# 🟢 一、中文部分：Promise 详解

### 1. 基本定义

**Promise** 是 JavaScript 中用于处理 **异步操作** 的一种对象。

它代表一个 **尚未完成但最终会完成或失败的操作** ，并返回结果值。

简单理解：

> Promise 就是一个“承诺”，告诉你：
>
> 我现在还没有结果，但将来一定会有（成功或失败），你可以提前告诉我结果出来后该做什么。

---

### 2. 为什么要用 Promise

在早期的 JS 代码中，异步操作通常使用  **回调函数（callback）** 。

例如：

```js
setTimeout(() => {
  console.log("完成！");
}, 1000);
```

但多层异步嵌套会导致所谓的  **“回调地狱（callback hell）”** ：

```js
doSomething(() => {
  doSomethingElse(() => {
    doThirdThing(() => {
      console.log("结束");
    });
  });
});
```

**Promise** 通过更清晰的链式写法解决这个问题：

```js
doSomething()
  .then(doSomethingElse)
  .then(doThirdThing)
  .then(() => console.log("结束"))
  .catch(err => console.error(err));
```

---

### 3. Promise 的三种状态

Promise 对象有三种状态（且 **只能单向变化** ）：

| 状态                | 含义                     | 状态改变                     |
| ------------------- | ------------------------ | ---------------------------- |
| **pending**   | 等待中（异步操作未完成） | 可变为 fulfilled 或 rejected |
| **fulfilled** | 成功（异步操作成功完成） | 状态固定                     |
| **rejected**  | 失败（异步操作失败）     | 状态固定                     |

一旦从 `pending` 变为 `fulfilled` 或 `rejected`，状态就 **不可逆** 。

---

### 4. 基本语法

创建一个 Promise：

```js
const promise = new Promise((resolve, reject) => {
  const success = true;
  if (success) {
    resolve("操作成功！");
  } else {
    reject("发生错误！");
  }
});
```

使用 Promise：

```js
promise
  .then(result => {
    console.log(result); // 输出: 操作成功！
  })
  .catch(error => {
    console.error(error); // 输出: 发生错误！
  })
  .finally(() => {
    console.log("操作结束");
  });
```

---

### 5. 常用方法

| 方法                             | 说明                                                      |
| -------------------------------- | --------------------------------------------------------- |
| `Promise.resolve(value)`       | 快速创建一个已成功的 Promise                              |
| `Promise.reject(reason)`       | 快速创建一个失败的 Promise                                |
| `Promise.all([p1, p2])`        | 等所有 Promise 成功后返回结果数组（有一个失败则整体失败） |
| `Promise.race([p1, p2])`       | 返回第一个完成（成功或失败）的结果                        |
| `Promise.allSettled([p1, p2])` | 等所有都完成（不论成功或失败）后返回状态数组              |
| `Promise.any([p1, p2])`        | 返回第一个成功的结果（若都失败则抛 AggregateError）       |

---

### 6. 链式调用与异步流程

每个 `.then()` 都返回一个新的 Promise，因此可以 **链式调用** 。

```js
fetchData()
  .then(data => process(data))
  .then(result => display(result))
  .catch(err => console.error("出错：", err));
```

---

### 7. async/await（Promise 的语法糖）

`async/await` 是基于 Promise 的语法糖，使异步代码看起来像同步：

```js
async function run() {
  try {
    const data = await fetchData();
    const processed = await process(data);
    console.log(processed);
  } catch (err) {
    console.error("出错：", err);
  }
}
```

---

### 8. 简单原理（实现思路）

Promise 内部实际上维护了：

* 一个 **状态变量** （pending / fulfilled / rejected）
* 一个**结果值**或**错误原因**
* 一组回调函数（存放 `.then()` 注册的回调）

  当 `resolve()` 或 `reject()` 被调用时，Promise 状态改变，并依次执行对应的回调。

---

### ✅ 小结

* Promise 是异步编程的基础；
* 它消除了“回调地狱”；
* 支持链式调用与错误统一捕获；
* 与 async/await 搭配使用最强大。

---

## 🟣 二、Русская часть: Подробно о Promise

### 1. Что такое Promise

**Promise** — это объект в JavaScript, представляющий  **асинхронную операцию** ,

которая может завершиться **успешно (fulfilled)** или  **с ошибкой (rejected)** .

Проще говоря:

> Promise — это "обещание": результат появится позже,
>
> и вы можете заранее указать, что делать в случае успеха или ошибки.

---

### 2. Зачем нужен Promise

До появления Promise использовались  **callback-функции** ,

но при вложенных вызовах получался т. н.  **"ад колбэков" (callback hell)** .

Promise делает код линейным и понятным:

```js
doSomething()
  .then(doSomethingElse)
  .then(finalStep)
  .catch(handleError);
```

---

### 3. Состояния Promise

Promise может находиться в одном из трёх состояний:

| Состояние | Значение                    | Переход                            |
| ------------------ | ----------------------------------- | ----------------------------------------- |
| `pending`        | ожидает результата | → fulfilled или rejected              |
| `fulfilled`      | выполнен успешно     | состояние фиксируется |
| `rejected`       | завершён с ошибкой  | состояние фиксируется |

После изменения состояния его уже нельзя поменять.

---

### 4. Синтаксис

```js
const promise = new Promise((resolve, reject) => {
  const success = true;
  if (success) {
    resolve("Успех!");
  } else {
    reject("Ошибка!");
  }
});

promise
  .then(result => console.log(result))
  .catch(error => console.error(error))
  .finally(() => console.log("Готово"));
```

---

### 5. Основные методы

| Метод                    | Назначение                                                              |
| ----------------------------- | --------------------------------------------------------------------------------- |
| `Promise.resolve(value)`    | Создаёт успешно завершённый Promise                      |
| `Promise.reject(reason)`    | Создаёт Promise с ошибкой                                          |
| `Promise.all([...])`        | Ждёт выполнения всех, при ошибке — отклоняет |
| `Promise.race([...])`       | Возвращает первый завершённый                          |
| `Promise.allSettled([...])` | Ждёт завершения всех, возвращает статусы       |
| `Promise.any([...])`        | Возвращает первый успешный результат             |

---

### 6. Цепочка `.then()` и обработка ошибок

`.then()` всегда возвращает новый Promise, поэтому можно выстраивать  **цепочки** :

```js
fetchData()
  .then(process)
  .then(show)
  .catch(err => console.error("Ошибка:", err));
```

---

### 7. async / await

Это синтаксический сахар над Promise — делает код "синхронным на вид":

```js
async function example() {
  try {
    const data = await fetchData();
    const result = await process(data);
    console.log(result);
  } catch (e) {
    console.error("Ошибка:", e);
  }
}
```

---

### 8. Принцип работы (внутренне)

Promise хранит:

* текущее состояние (`pending`, `fulfilled`, `rejected`);
* значение результата или причину ошибки;
* массив обработчиков (`then`, `catch`).

  Когда вызывается `resolve` или `reject`, состояние меняется и выполняются обработчики.

---

### ✅ Краткий вывод

* Promise — ключевой инструмент для работы с асинхронностью в JS;
* Устраняет "callback hell";
* Поддерживает цепочки и централизованную обработку ошибок;
* `async/await` делает работу с ним ещё удобнее.
