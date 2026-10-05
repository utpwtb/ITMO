# HTTP Coroed：协程 HTTP 服务器

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/corohttp/README.md)。

给定一个采用有栈协程（stackful coroutine）的简单框架 [Coroed](https://github.com/vityaman-edu/coroed)。任务是为其加入异步 I/O，并以此实现简单的 HTTP 服务器。

## 异步 I/O

问题：常规 `read` / `write` 会阻塞线程，降低服务器效率，也抵消协程的优势。必须使用操作系统提供的 API 实现非阻塞 I/O。

从协程视角看，对应的读写接口应像熟悉的“阻塞”调用一样使用；发生 I/O 等待时，协程进入等待状态，其线程转而执行另一个已经就绪的协程。

研究 Linux 中现有的异步 I/O 方案，例如 `aio`、`epoll`、`io_uring`，选择最适合的方案。

使用 libc 函数时要小心：部分函数可能使用线程局部变量，因此基于 `alarm` 的抢占式多任务机制可能产生问题。

## HTTP

I/O API 完成后，实现简单 HTTP 服务器。请求 `/hello/<name>` 时，返回 JSON 对象，其中字段 `message` 的值为 `<name>`。

## 性能测试

再实现一个仅使用线程的 HTTP 服务器：一个请求对应一个线程。设计性能测试，将其结果与 Coroed 版本比较。
