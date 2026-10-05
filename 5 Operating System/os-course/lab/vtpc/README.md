# 基础路线：实验 2（用户态页缓存）

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtpc/README.md)。

## 任务

操作系统使用页缓存优化块设备访问，缓存读取和写入磁盘的数据。再次访问时，可以操作 RAM 中的数据而不是磁盘，避免较高的延迟。可回顾[存储层次金字塔，第 35 页][memory-pyramid-csbasics]与[程序员需要了解的内存知识][what-every-programmer-should-know-about-memory]。

本实验要求在用户空间以**动态库**形式实现块缓存。页面置换策略及其他任务要素由教师指定。

实现类似系统 API 的简单文件接口：

1. 按路径打开可读文件，返回文件句柄。例如 `int vtpc_open(const char *path)`。
2. 按句柄关闭文件。例如 `int vtpc_close(int fd)`。
3. 从文件读数据。例如 `ssize_t vtpc_read(int fd, void buf[.count], size_t count)`。
4. 向文件写数据。例如 `ssize_t vtpc_write(int fd, const void buf[.count], size_t count)`。
5. 移动文件数据位置指针，只需支持绝对位置。例如 `off_t vtpc_lseek(int fd, off_t offset, int whence)`。
6. 将缓存数据同步到磁盘。例如 `int vtpc_fsync(int fd)`。

实现的块缓存访问磁盘时，必须**绕过操作系统的页缓存**。

为验证功能，需要改造教师指定的实验 1 负载程序，使它使用你的缓存。运行并确认正确，比较加入缓存前后的性能。

模块入口是 `vtpc.h` 和 `vtpc.c`。测试框架调用这个 API，将 `vtpc` 与 libc 的行为比较。[头文件](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtpc/lib/vtpc.h)、[实现模板](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtpc/lib/vtpc.c)位于远程仓库。

## 限制

1. 程序或程序组使用 C 语言。
2. 若变体为 Optimal，则须让用户告诉页缓存何时再次访问数据。可向 `read` / `write` 加参数，例如 `ssize_t vtpc_read(int fd, void buf[.count], size_t count, access_hint_t hint)`，或增加 API，例如 `int vtpc_advice(int fd, off_t offset, access_hint_t hint)`。`access_hint_t` 表示绝对时间或时间间隔，用于判断下次访问时间。
3. 禁止使用系统调用之上的高级抽象。

## 报告与答辩要求

报告包含：

1. 封面：实验编号、名称、学生姓名、实验课教师姓名、班级、变体。
2. 所分配变体的任务文本。
3. 简要代码概述。
4. 负载程序使用自制页缓存之前、之后的运行数据。
5. 分析结果并给出结论。

## 变体说明

变体是课程讲授的页置换算法名称（见[操作系统第 3 部分第 22 页][page-preemtion-algo-slides]），也可由教师另外指定。例如：

- LRU：最近最少使用。
- LFU：最不经常使用。
- MRU：最近最多使用。
- FIFO：先进先出。
- NRU：最近未使用。
- Clock：时钟算法。
- Optimal：最优置换，带下次访问提示。
- Random：随机置换。
- Second chance：第二次机会。
- ARC：自适应替换缓存。
- 2Q：双队列策略。
- LRU-K：考虑最近 K 次访问历史的 LRU 扩展。

> [!NOTE]
> 上述只是**置换**算法，页面还必须正确**加载**。思考接下来应该加载哪一页、在什么时机加载。

> 译者注：上面的 `void buf[.count]` 是原文的接口示意记法。实际实现请遵循仓库 `vtpc.h` 的有效 C 声明。当前 `vtsh` 文档没有具体指定这里提到的“实验 1 负载程序”；应向教师取得，而不能把缺失信息当作已提供。

> 译者源码核对：任务要求动态库，但当前 `lib/CMakeLists.txt` 写的是 `STATIC`，模板代码只是直接转发 libc，并没有实现缓存。头文件的 `vtpc_open` 实际有 `path`、`mode`、`access` 三个参数。请保持测试接口兼容，同时完成任务要求。

[memory-pyramid-csbasics]: https://se.ifmo.ru/documents/10180/640663/%D0%9F%D1%80%D0%B5%D0%B7%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F+%D0%BB%D0%B5%D0%BA%D1%86%D0%B8%D0%B9+2019+%D1%87%D0%B0%D1%81%D1%82%D1%8C+2.pdf/a89541ff-090d-47b4-8454-eb5d71afd207
[what-every-programmer-should-know-about-memory]: https://www.akkadia.org/drepper/cpumemory.pdf
[page-preemtion-algo-slides]: https://se.ifmo.ru/documents/10180/1505608/%D0%9E%D0%BF%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5+%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B.+%D0%A7%D0%B0%D1%81%D1%82%D1%8C+3.pdf/188c34ff-f76c-1d42-b3cb-f9314b5898d8
