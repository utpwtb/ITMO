# 操作系统实验中的 Linux 监控工具

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/doc/experiments/monitoring.md)。
>
> 操作系统课程通用指南：哪些工具采集哪些指标，以及如何理解输出。适用于所有实验；将 `<program>` 替换为被测程序。

实验监控有两种不同用途，务必区分：

1. **特征分析**：在规划测量前，采集系统信息，理解程序的基本行为。此时允许使用开销较大的工具，例如 `perf stat`、持续运行的 `vmstat`。
2. **最终测量**：采集指标时尽可能减少干扰，避免监控本身改变测量时间。见 [statistics.md](statistics.md) 的测量工具干扰部分。

## 系统基本信息（实验开始时采集一次）

| 命令 | 提供的信息 |
|---|---|
| `uname -a` | 内核、体系结构 |
| `lscpu` | CPU 型号、核心/线程数、频率、指令集标志（avx、sse 等） |
| `lscpu -e` | 逻辑 CPU ↔ 物理核心 ↔ 插槽拓扑，用于 `taskset` 和 SMT 分析 |
| `cat /proc/cpuinfo \| grep -i cache` | 原文：L1/L2/L3 缓存容量 |
| `free -h` | RAM 容量、使用情况、页缓存/缓冲区大小 |
| `sudo lshw -class disk -class memory -short` | 磁盘/内存型号、总线类型 |
| `sudo smartctl -a /dev/sdX` | 存储设备类型（SSD/HDD/NVMe）及状态 |
| `cat /sys/block/sdX/queue/rotational` | `0` 为非旋转设备（SSD/NVMe），`1` 为 HDD |
| `nproc` | 可用逻辑 CPU 数 |
| `numactl --hardware` | NUMA 拓扑（适用时） |

## 运行期间或运行后的监控

### `/usr/bin/time -v <program> ...`

用于获取单个进程时间等指标的简单工具。请使用 `/usr/bin/time`，而非 Bash 内置的 `time`；内置版本没有 `-v`，指标也更少。

一次运行可获得：实际经过时间（wall clock）、用户态时间、内核态时间、最大 RSS、自愿/非自愿上下文切换、次要/主要缺页，以及文件 I/O 操作（如果内核按进程统计这些数据）。

### `perf stat -e <events> <program> ...`

更灵活，可使用硬件与软件计数器：

```bash
perf stat -e task-clock,context-switches,cpu-migrations,page-faults,\
cache-references,cache-misses,cycles,instructions \
  taskset -c 2 <program> ...
```

- `context-switches`：进程离开 CPU、发生上下文切换的次数。
- `cpu-migrations`：进程迁移到其他核心的次数；正确使用 `taskset` 后通常接近 0。
- `cache-misses` / `cache-references`：CPU 缓存未命中与引用。
- `page-faults`：次要与主要缺页之和，是 `mmap` 和虚拟内存实验的重要指标。
- 更专门的内存实验可使用 TLB 计数器：`dTLB-load-misses`、`dTLB-store-misses`。用 `perf list` 查看可用事件。

`perf stat` 自身会引入开销。原文要求：大规模最终时间测量不要以它为 wall time 来源，只在特征分析阶段使用。

### 系统级观察工具（另开终端并行运行）

```bash
vmstat 1        # 空闲内存、缓冲区/缓存、swap、CPU %us/%sy/%id、块 I/O（bi/bo）
mpstat -P ALL 1 # 分别观察每个逻辑 CPU 的负载；辅助检查迁移
pidstat -urd 1  # 按 PID 观察 CPU、内存、磁盘（sysstat 软件包）
iostat -x 1     # 存储设备负载：%util、await（延迟）、r/s、rkB/s
```

理解 `iostat -x`：

- `%util` 接近 100%：原文认为磁盘成为瓶颈。
- `await`：平均请求延迟，单位毫秒。
- `r/s`、`rkB/s`：每秒读取操作数与读取量。

### 制造后台负载：`stress-ng`

可以先展示资源竞争下“受干扰”的测量，再学习如何隔离干扰，见 [environment.md](environment.md)。

```bash
stress-ng --cpu 2 --io 1 --vm 1 --vm-bytes 256M --timeout 30s
```

- `--cpu N`：N 个 CPU 负载工作进程。
- `--io N`：N 个调用 `sync()` 的工作进程。
- `--vm N --vm-bytes SIZE`：内存子系统负载工作进程及其内存规模。

后台运行 `stress-ng` 时，非自愿上下文切换、CPU 迁移和 wall time 波动通常增加，可直观说明隔离环境的必要性。

## 指标与工具对照

| 指标 | 主要工具 | 替代/补充 |
|---|---|---|
| 实际经过时间（Wall time） | `/usr/bin/time -v` | 原文列出 `perf stat`（task-clock）、程序内计时器、shell `time` |
| 用户态/内核态时间 | `/usr/bin/time -v` | `perf stat -e task-clock`、`/proc/[pid]/stat` |
| 即时 %CPU | `pidstat -u 1`、`top` | `mpstat -P ALL 1` |
| 上下文切换 | `/usr/bin/time -v` | `perf stat -e context-switches` |
| CPU 迁移 | `perf stat -e cpu-migrations` | — |
| 次要/主要缺页 | `/usr/bin/time -v` | `perf stat -e page-faults`、`/proc/[pid]/stat`（`minflt`、`majflt`） |
| RAM/RSS | `/usr/bin/time -v`（Maximum RSS） | `pidstat -r 1`、`/proc/[pid]/status`（`VmRSS`） |
| 磁盘 I/O 与延迟 | `iostat -x 1` | `pidstat -d 1` |
| CPU 缓存未命中 | `perf stat -e cache-misses,cache-references` | — |
| TLB 未命中 | `perf stat -e dTLB-load-misses,dTLB-store-misses` | 用于虚拟内存实验 |
| 页缓存状态 | `free -h` | `cat /proc/meminfo`（`Cached`、`Buffers`） |

## 工具自身的干扰

监控工具本身也是进程，或像 `strace` 那样改变被测进程行为。它会消耗 CPU/内存，引入额外系统调用或中断。应明确验证：同一配置分别在开销较大的工具下（`perf stat`、`strace -c`）及不使用这些工具时运行，比较 wall time。若差异相对置信区间不可忽略，最终测量应使用更轻量的方法。详见 [statistics.md](statistics.md)。

> 译者技术提示：`task-clock` 是任务消耗的 CPU 时间，不等于实际经过时间；多线程时尤其不能混用。`%util≈100%` 对支持并行请求的 SSD/NVMe 不能单独作为饱和判据。`/proc/cpuinfo` 也不保证完整列出每级缓存容量，需结合实际输出核对。表中保留了原文工具列表。
