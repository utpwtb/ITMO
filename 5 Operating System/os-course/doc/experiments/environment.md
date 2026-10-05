# 实验环境的配置与隔离

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/doc/experiments/environment.md)。
>
> 操作系统课程通用指南。适用于测量程序执行时间、调度器行为、资源消耗或其他操作系统指标的任务，无论实验受 CPU、I/O 还是内存限制。

## 1. 为什么要控制环境

在真实操作系统中，时间和资源测量会受到与研究对象无关的噪声影响：后台进程、CPU 频率变化、跨核迁移、缓存状态（CPU 缓存、文件缓存、TLB）。本文提供消除或控制这些噪声的检查清单。并非每个实验都需要所有措施；应选择适合任务的措施，并在报告中明确记录。

## 2. 后台进程

开始一组测量前，关闭不必要的程序：浏览器、IDE、云文件夹同步、索引服务（`mlocate`/`plocate`、`tracker`）、软件包更新。

```bash
uptime                 # 空闲机器的 load average 应接近 0
top -bn1 | head -20     # 查看进程 %CPU 和后台负载
```

如果实验平台是云端虚拟机，就无法控制物理主机上的“邻居”。教学实验可以接受，但解释结果时必须说明这一限制。更严格的实验宜使用裸机，或将 vCPU 固定分配的独占虚拟机。

## 3. CPU 频率（DVFS）与 Turbo Boost

现代 CPU 根据负载和温度动态改变频率，导致不同运行之间不稳定，尤其影响 CPU 密集型实验。

```bash
cpupower frequency-info                      # 当前 governor 和频率范围
sudo cpupower frequency-set -g performance   # 原文：固定为最高频率
```

频率调节策略（见 `man cpupower`）：`performance`（原文称固定最高频率，推荐用于实验）、`powersave`、`ondemand`/`schedutil`（动态策略，会引入噪声）。

可选：控制 Intel Turbo Boost / AMD Precision Boost：

```bash
cat /sys/devices/system/cpu/intel_pstate/no_turbo    # 0 表示 turbo 已启用
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo   # 关闭
```

若硬件或权限不支持，请在报告中明确说明未控制 Turbo Boost，并在解释波动时考虑这一点。

## 4. 将进程绑定到 CPU（`taskset`）

不显式绑定时，调度器可能让进程跨核迁移（`perf stat` 中的 `cpu-migrations`）。不同核心的 L1/L2 缓存状态以及当前频率可能不同。

```bash
taskset -c 2 ./your_program ...      # 将新进程绑定到核心 2
taskset -cp 2 <pid>                  # 将已运行进程绑定到核心 2
```

选择核心前，查看 `mpstat -P ALL 1`，避免选中处理大量中断的核心（通常是 CPU0）。

研究多线程/多进程交互时，例如同步或调度实验，将任务绑定到不同核心也是实验设计的一部分：应有意识地决定研究单核、同一插槽的多个核心，还是不同插槽（NUMA）的行为。

## 5. 调度优先级（`nice` / `renice`）

优先级影响资源竞争时调度器为进程分配 CPU 的倾向。

```bash
sudo nice -n -5 taskset -c 2 ./your_program ...   # 负 nice 值表示更高优先级，需要 root
renice -n -5 -p <pid>                             # 修改已有进程的优先级
```

范围为 `-20`（最高优先级）到 `19`（最低优先级）；原文要求负值使用 root 权限。这可进一步减少实验进程被其他任务抢占的影响。

## 6. 缓存状态：内存或磁盘实验

若程序读取文件或处理大量数据，文件页缓存、CPU 缓存和 TLB 状态可能极大地改变结果，也决定了实际测量的对象。必须有意识地选择缓存状态，并在同一配置的整组实验中保持一致。

**冷缓存**：每次运行前清除页缓存中的数据：

```bash
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches
```

`1` 仅清理 page cache，`2` 清理 dentries/inodes，`3` 清理两者。

这种模式测量实际访问磁盘/内存的代价；访问模式局部性的差异通常更明显。

部分教学程序提供缓存控制选项，例如 `--no-cache`，通过 `O_DIRECT`、`posix_fadvise` 或平台专用 API 实现。若有此选项，优先使用它而不是手工执行 `drop_caches`：可跨 Linux/macOS 使用，也不要求 root。依赖它作结论之前，先看 `--help` 或源代码，确认具体行为。

**热缓存**：只预热一次，随后整组测量不再清理缓存。这测量的是访问已缓存数据的效率。

**不能做的事**：在同一配置的不同运行之间交替使用冷热缓存，却没有把它作为独立实验因素说明。否则，波动反映的是缓存状态，而非研究的效应。

## 7. 工作数据集相对 RAM/缓存的大小

冷缓存实验的数据规模不必超过 RAM，但必须足够大，使执行时间不被噪声淹没；按实际程序选择，例如每次运行达到秒级而非微秒级。

热缓存实验若要保留磁盘/内存层面的明显差异，而不只是测量从热缓存复制数据的速度，工作集应显著**大于**对应层级的缓存容量，例如 page cache 或 CPU LLC。

## 8. 进阶隔离（可选）

更严格的实验可以使用：

- 内核启动参数 `isolcpus=<N>`：原文将其描述为把核心 N 从操作系统通用调度器中隔离出来。
- cgroups v2（`cpuset`、`cpu.max`、`memory.max`）：无需重启即可限制和隔离资源。
- 关闭 SMT/Hyper-Threading：同一物理核心的另一个逻辑 CPU 可能造成干扰。用 `lscpu -e` 查看逻辑 CPU 到物理核心的对应关系。
- 考虑 NUMA 拓扑：`numactl --hardware`、`numactl --cpunodebind=0 --membind=0 ./your_program`。对于多插槽机器上同时使用 CPU 与内存的实验尤其重要。

基础任务不强制要求这些措施；它们适用于解释基础配置后的剩余波动，或专门研究 NUMA/核心隔离的任务。

## 9. 开始整组测量前的检查清单

- [ ] 关闭后台程序，`uptime` / `top` 显示机器空闲。
- [ ] 若频率影响实验，设定 CPU governor 为 `performance`。
- [ ] 确定是否控制 Turbo Boost，并记录。
- [ ] 若与实验相关，使用 `taskset` 绑定具体核心。
- [ ] 若使用 `nice` / `renice`，设定进程优先级。
- [ ] 若适用，选定缓存状态方法，并在整组测量中保持一致。
- [ ] 若适用，说明工作集规模相对 RAM/缓存的选择依据。
- [ ] 在整组测量前后保存系统状态“快照”。

> 译者技术提示：`performance` 不保证在所有硬件和驱动上严格固定最高频率；上述关闭 turbo 的路径属于 Intel 驱动接口，不能直接当作通用 AMD 命令。`drop_caches` 不等于清空 CPU 缓存、TLB 或所有设备缓存。`isolcpus` 也不自动隔离全部中断和内核活动。这些提示用于区分原文的简化表达与实际机制。
