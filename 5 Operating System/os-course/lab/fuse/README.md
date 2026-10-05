# FUSE：用户态文件系统

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/fuse/README.md)。

本实验学习 [libfuse](https://github.com/libfuse/libfuse)。它支持在用户空间实现文件系统，比开发内核模块更简单。注意，该库有 Python 绑定。

思考可以通过文件系统 API 提供哪些服务，例如浏览 GitHub 仓库、访问数据库对象、访问聊天软件中的会话。

选定想实现的功能，与教师协商后，实现自己的文件系统。

允许使用大语言模型生成与外部服务交互的代码。生成代码必须放在独立、隔离的软件模块中，并在报告中明确说明使用大语言模型的方法。
