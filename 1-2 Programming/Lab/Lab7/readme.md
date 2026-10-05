注意！不同版本的作业要求文本不同！

请按以下要求对第六次实验作业的程序进行改进：

1. 将集合的存储改为使用关系型数据库管理系统（PostgreSQL）。取消集合的文件存储方式。
2. 使用数据库的功能（sequence）来生成 `id` 字段。
3. 只有在对象成功添加到数据库后，才更新内存中集合的状态。
4. 所有获取数据的命令都必须操作内存中的集合，而不是数据库。
5. 实现用户的注册和登录功能。用户应能设置密码。
6. 存储密码时，使用 SHA-512 算法进行哈希处理。
7. 禁止未登录用户执行任何命令。
8. 存储对象时，需保存创建该对象的用户信息。
9. 用户应能查看集合中的所有对象，但只能修改自己拥有的对象。
10. 通过在每个请求中发送用户名和密码来识别用户身份。
11. 必须实现请求的多线程处理。

多线程处理的具体要求如下：

* 使用创建新线程（`java.lang.Thread`）的方式实现请求的多线程读取。
* 使用 `ForkJoinPool` 实现接收到的请求的多线程处理。
* 使用可缓存线程池（Cached thread pool）实现响应的多线程发送。
* 使用 `java.util.concurrent.locks.ReentrantLock` 的读写同步机制来保证对集合的访问同步。

作业执行步骤：

* 使用 PostgreSQL 作为数据库。
* 连接教研室服务器上的数据库时，主机名为 `pg`，数据库名为 `studs`，用户名和密码与连接服务器时使用的相同。

实验报告必须包含以下内容：

* 作业要求文本。
* 所开发程序的类图。
* 程序的源代码。
* 实验总结。
* 第六次实验答辩问题：
  * 多线程。`Thread` 类，`Runnable` 接口。`synchronized` 修饰符。
  * `Object` 类的 `wait()` 和 `notify()` 方法，`Lock` 和 `Condition` 接口。
  * `java.util.concurrent` 包中的同步工具类。
  * `volatile` 修饰符。原子数据类型和原子操作。
  * `java.util.concurrent` 包中的集合类。
  * `Executor`，`ExecutorService`，`Callable`，`Future` 接口。
  * 线程池。
  * JDBC。与数据库交互的步骤。`DriverManager` 类。`Connection` 接口。
  * `Statement`，`PreparedStatement`，`ResultSet`，`RowSet` 接口。
  * 设计模式。
