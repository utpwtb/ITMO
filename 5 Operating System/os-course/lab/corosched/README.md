# CoroSched：协程调度器

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/corosched/README.md)。原文标题拼写为 `CoroShed`。

给定采用有栈协程的简单框架 [Coroed](https://github.com/vityaman-edu/coroed)。任务是改进任务调度器。

原始 Coroed 调度器将任务保存在数组中，导致任务数量受限，而且调度不公平。请实现反馈式（feedback）任务调度器。

测试新调度器的性质，并与初始实现进行比较。

> 译者注：原文只提出“feedback 调度器”，未指定队列层级、时间片、优先级更新公式等细节；这些不能当作仓库已经给出的硬性要求。
