# Introductory Experiment：操作系统课程实验入门

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/README.md)。附带 PDF 的不同表述见 [PDF 差异补译](PDF差异补译.md)。

实验变体由以下参数组成，它们决定比较方式：

| 参数 | 说明 |
|---|---|
| Read/Write | 比较的负载类型：读取或写入 |
| Cache/No cache | 内存访问方式：使用系统缓存或不使用 |
| Size | 测试文件大小 |
| Seq/Rand | 随机访问或顺序访问模型 |

变体含义示意见[原文配图 exp-variants.png](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/img/exp-variants.png)。

两张配图的标签和七种比较方案已整理为[附图中文说明](附图中文说明.md)。

> [!TIP]
> 通用实验指南：
> - [环境配置与隔离](../../doc/experiments/environment.md)。
> - [监控工具及其输出](../../doc/experiments/monitoring.md)。
> - [置信区间与测量次数 N](../../doc/experiments/statistics.md)。

现代操作系统提供两种本质不同的文件访问方式：

1. 使用常规 `read()` / `write()`，用 `lseek()` 改变文件位置。
2. 使用 `mmap()` 把文件映射到内存。

理解这两种方式的能力和限制，对数据处理应用开发非常重要。

本任务的数据模型以图的顶点表示记录，通过沿顶点之间的链接遍历访问数据。顶点在文件中位置固定，可能离其邻居很近，也可能很远。

[原文数据模型图 model.png](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/img/model.png)。

我们不特别关心具体存储格式和空间占用，关键是数据可能位于文件中相邻或相距很远的位置，对应磁盘访问位置也不同。

## 0. 实验目标

通过实验比较给定原型程序的运行时间，模拟典型数据处理负载：按**顺序/随机**次序**读取/更新**磁盘中的记录。

同时学习正确开展操作系统实验：固定环境、选择工具、规划测量次数、统计处理结果，而不是凭 1–3 次运行“目测”下结论。这些基础原则也适用于职业研究或毕业论文。

## 1. 研究对象

每个实验的最终指标是一个数：**图顶点遍历时间的估计值**。

参与实验的程序位于远程仓库：

- [lab/util/graphgen.py](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/util/graphgen.py)：参数化图生成器，将数据结构序列化到二进制文件。
- [src/graph_traverse.c](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/src/graph_traverse.c)：通过 `read()` / `lseek()` 遍历图。
- [src/graph_traverse_mmap.c](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/src/graph_traverse_mmap.c)：相同遍历逻辑，使用 `mmap()`。

两种程序的命令行格式：

```sh
<app> [--write] [--no-cache] <iterations> <file1> [file2 ...]
```

- `--write`：写入模式，修改访问到的顶点数据。
- `--no-cache`：禁用系统缓存；`mmap()` 情况有细节差异。
- `<iterations>`：重复遍历次数，用于延长运行时间。
- `[file2 ...]`：额外遍历文件，也可延长运行时间，但方式不同。

> [!NOTE]
> 不必深入研究 `--no-cache` 的实现；若感兴趣，可阅读远程源码 [graph_io.h](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/src/graph_io.h) 与 [graph_traverse_mmap.c](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/intro-exp/src/graph_traverse_mmap.c) 的注释。

> 译者源码核对：当前 `graph_traverse` 在 Linux 使用 `O_DIRECT`，macOS 使用 `F_NOCACHE`，FreeBSD 的 `O_DIRECT` 仅为建议；失败不会自动回退为缓存 I/O。Linux 的对齐处理可能增加传输量。当前 `mmap` 版本的 `--no-cache` **仅发送 `MADV_RANDOM` 提示，仍使用页缓存**，不保证冷缓存，也不会清除系统或磁盘缓存。报告必须区分这两种含义。

## 2. 准备测试数据

生成相同大小、相同 `seed`、但不同拓扑的两个图。

**随机物理顺序**：链表遍历所有记录，但链表中的相邻记录通常位于不同文件页：

```sh
python3 ../util/graphgen.py -s 10M --seed 427 --topology chain -b 0.5 --min-step-pages 2 -o graph-rand.bin
```

**顺序物理顺序**：记录 i 指向 i+1，因此遍历顺序与文件中的记录顺序一致：

```sh
python3 ../util/graphgen.py -s 10M --seed 427 --topology sequential -o graph-seq.bin
```

参数详见 `--help`，简要说明：

- `-s`：图文件大小。
- `--seed`：生成随机种子。
- `--topology`：最终图结构，顺序线性或随机线性。

> [!CAUTION]
> `graph-seq.bin` **不能使用 `--topology chain`**。`chain` 描述图的链状结构，却刻意将路径放在随机的物理偏移顺序中；旧任务说明曾有此错误。

## 3. 编译程序

两种程序面向 Linux、macOS 和 FreeBSD，需要安装 `clang` 或 `gcc`。

```sh
mkdir -p out
clang -o out/graph_traverse src/graph_traverse.c
clang -o out/graph_traverse_mmap src/graph_traverse_mmap.c
```

## 4. 阶段一：研究 `graph_traverse`（read/lseek）

以下测量工具示例**面向 Linux**，其他操作系统需使用对应工具。

### 4.1. 采集系统信息

尽可能收集与实验有关的重要信息，使实验可复现，也便于正确解释数据。

工具说明见[监控指南](../../doc/experiments/monitoring.md)的系统信息部分：`uname -a`、`lscpu`、`lscpu -e`、`free -h`、磁盘用 `lshw` / `smartctl`，以及 `nproc`。

无法获得信息时，在报告中写明原因，不能用猜测替代未知参数。所收集的信息是后续结论的依据，绝不能省略。

> [!NOTE]
> 在虚拟机中，部分命令输出不完整或只有概括信息是正常现象。思考为什么某些参数可见、另一些不可见。
>
> 可尝试从宿主系统等其他来源获得缺失信息，但必须标明来源，不能把虚拟设备参数当作物理宿主机参数。

### 4.2. 准备环境

准备自己的“实验室”：结束后台任务、设定 CPU governor、绑定核心、清理或预热系统缓存。详见[环境指南](../../doc/experiments/environment.md)。

干扰较少的环境使结果更可信、可复现。无法排除的干扰应记录在报告中，并在解释测量时考虑。

### 4.3. 初步基线测量

每个图先运行一次，观察行为。再尝试禁用缓存和修改数据模式：

```sh
time ./out/graph_traverse 1 graph-rand.bin
time ./out/graph_traverse 1 graph-seq.bin

time ./out/graph_traverse --no-cache 1 graph-rand.bin
time ./out/graph_traverse --no-cache 1 graph-seq.bin

time ./out/graph_traverse --write 1 graph-rand.bin
time ./out/graph_traverse --write 1 graph-seq.bin

time ./out/graph_traverse --write --no-cache 1 graph-rand.bin
time ./out/graph_traverse --write --no-cache 1 graph-seq.bin
```

若所分配变体中的某个场景运行太久（超过 20–30 秒），可在合理范围内调整图文件大小；运行时间也不应接近 0。

> [!NOTE]
> 在虚拟机、WSL 或 Docker 中实验时，图文件应放在来宾系统主要磁盘分区的目录中，例如家目录 `~/`。Windows/macOS 上的这些技术也可能使用虚拟化。
>
> 若使用与宿主机共享的目录，访问会经过许多额外虚拟化层。

观察 `usr` / `sys` 时间比例，即 User/Kernel Time 指标。原文预期写入模式因修改页回写而有更多 `sys time`。用 `strace` 研究不同模式的行为，并使用其选项方便比较。

更详细的分析使用 `/usr/bin/time -v` 和 `perf stat`：观察 `context-switches`、`cpu-migrations`、`page-faults`、`cache-misses`，见[监控指南](../../doc/experiments/monitoring.md)。

在后台负载存在时重复一次运行，观察“有噪声”的测量。可用 `stress-ng` 或类似基准工具制造负载。把观察记录到报告中。

### 4.4. 提出假设

明确写出预期及理由，例如：

- HDD 的差异比 SSD/NVMe 更明显，因为磁头需要定位。
- 较小文件在各配置下遍历更快。

思考哪些因素与操作系统机制和所分配实验变体最相关。

### 4.5. 制定实验计划

测试前先确定如何执行。顺序和次数会影响结果，例如 CPU 升温后降频、后台任务启动等。

因此，不要分块连续运行完一个配置再运行另一个；应交错运行不同配置，以减少系统性漂移。

报告中记录：

1. 每次运行使用什么指标。
2. 缓存预热/清理方法，同一配置的整组测量保持一致。
3. 重复次数 N 与执行顺序。
4. 舍弃多少次初始预热运行及原因；须在查看结果**之前**决定。
5. 区分测量与监控；写入最终报告的测量组使用干扰最小的方式。

N 的依据与置信区间详见[统计指南](../../doc/experiments/statistics.md)。

### 4.6. 开始前记录环境

最终测量前再次执行 4.1，保存“前快照”：`uptime`、`top -bn1`，若可获取则记录温度/降频情况。确认环境没有变化，仍然稳定。

### 4.7. 执行整组测量

手工测量缓慢而枯燥，应使用 shell 脚本自动化，也可单独检查自动化是否影响结果。

下面是 AI 生成的 Linux 数据采集脚本示例。**请自行编写自己的脚本。**

```bash
#!/usr/bin/env bash
set -euo pipefail

CORE=2
N=30
ITER=5
OUT=results_read.csv
echo "timestamp,graph,run_id,wall_time_s,user_time_s,sys_time_s,vol_ctx,invol_ctx,minflt,majflt" > "$OUT"

graphs=(graph-seq.bin graph-rand.bin)
for i in $(seq 1 "$N"); do
  for g in "${graphs[@]}"; do
    ts=$(date +%s)
    /usr/bin/time \
      -f "$ts,$g,$i,%e,%U,%S,%w,%c,%R,%F" \
      -a -o "$OUT" \
      taskset -c "$CORE" ./out/graph_traverse --no-cache "$ITER" "$g" \
      > /dev/null
  done
done
```

采集脚本必须：保存每次运行的原始数据[^enough-data]，而非只有平均值；保存足够的复现元数据，包括图文件名、`--no-cache` / `--write`、迭代次数、`taskset`；完整提交，并能在答辩时重新运行。

不用把日志直接塞进报告正文，需要时放到附录。

[^enough-data]: 规模应合理，不需要保存数十或数百 GB 的日志。

### 4.8. 分析测量

对比较的配置计算平均时间、标准差、置信区间，见[统计指南](../../doc/experiments/statistics.md)。明确说明异常值和预热如何处理。

将两组测量的分布叠加在**同一张图**（layered plot）中，可以使用直方图或 KDE（核密度估计）。它们有什么区别？通过图形直观看到测量差异，也理解为什么不能简单假定分布“正态”。

### 4.9. 给出结论

明确回答：

1. **比较**：哪个更大/更小，相差多少？是否符合 4.4 的假设？若不符合，什么操作系统/硬件机制能解释？
2. **误差**：置信区间宽度是否合适？比较的区间是否重叠？
3. **充分性**：再增加 N 次测量是否有帮助？至少用通用指南公式粗略估计。

## 5. 阶段二：研究 `graph_traverse_mmap`

对 `graph_traverse_mmap` 重复 4.1–4.9，参照阶段一，自行编写采集脚本：

```sh
./out/graph_traverse_mmap --write --no-cache 1 graph-seq.bin
./out/graph_traverse_mmap --write --no-cache 1 graph-rand.bin
```

注意差异：

- 比较 `read()` / `lseek()` 与 `mmap()` 的上下文切换次数和缺页次数，解释观察，并用于测量分析。
- 应允许结论与阶段一**不同**，这正是再次研究的价值。不要调整方法去强求相同结论。

## 6. 阶段三：最终比较与总体结论

把所有测量组的图放在一起：`graph_traverse` 两组、`graph_traverse_mmap` 两组，进行定性与定量比较。

总体结论应回答：

- 哪些测量条件至关重要，哪些可以忽略？例如 `taskset` 很重要，而图全部进入缓存时具体磁盘型号可能不重要。必须使用自己的实际观察。
- 测量工具本身有多大干扰？使用 `perf stat` / `strace` 与只用 `time` / `/usr/bin/time` 时，遍历时间是否不同？见[统计指南第 8 节](../../doc/experiments/statistics.md)。

## 7. 提交内容

1. 带实际选项的图生成脚本，以及阶段一、二的采集脚本，必须可复现地运行。
2. 全部四组的原始数据，使用 CSV 或类似格式。
3. 数据处理脚本/Notebook。
4. 报告：系统信息、环境配置、假设、N 与缓存方法的依据、比较四组结果的表格和图。

> [!IMPORTANT]
> 不要把所有东西放入报告！脚本和日志单独放在附录，正文只保留**关键内容**。详见[报告规则](../../doc/report.md)。

## 8. 答辩要求

按要求准备：

- 在任意可用机器展示、重新运行采集脚本，包括通过 `graphgen.py` 生成图。
- 解释环境配置的每一个选择。
- 解释置信区间如何计算，以及增减 N 对结论的影响。
- 根据 RAM 容量与缓存方法，说明图大小 `-s` 的选择依据。

## 9. 补充材料

- [实验设计视频指南](https://youtu.be/0VKhPE1lWos)。
- [环境配置](../../doc/experiments/environment.md)。
- [监控工具](../../doc/experiments/monitoring.md)。
- [统计处理](../../doc/experiments/statistics.md)。
- `man`。
