# WebLab3 — JMX 监控与分析实验指导

---

## 实验任务 1：运行并验证 MBean 功能

### 1.1 新增文件结构

任务 1 在项目中新增了以下文件：

```
src/main/java/com/itmo/jmx/
├── PointsStatisticsMBean.java   ← MBean 接口（暴露的属性/操作）
├── PointsStatistics.java        ← MBean 实现（统计逻辑 + 通知）
├── AreaCalculatorMBean.java     ← MBean 接口
├── AreaCalculator.java          ← MBean 实现（面积计算公式）
└── JMXConfig.java               ← @WebListener，启动时注册 MBean
```

并修改了一个文件：

```
src/main/java/com/itmo/bean/ResultsBean.java  ← addPoint() 中添加了 MBean 通知调用
```

### 1.2 编译并部署

```bash
# 在项目根目录下编译
mvn clean package

# 将生成的 target/WebLab3-1.0-SNAPSHOT.war 部署到 WildFly
# 方式一：复制到 WildFly 的 standalone/deployments/ 目录
# 方式二：通过 IDEA 的 Run Configuration 直接部署
```

### 1.3 确认 MBean 已注册

部署成功后，在 WildFly 控制台日志中应能看到：

```
INFO  [com.itmo.jmx.JMXConfig] Registered MBean: com.itmo:type=PointsStatistics
INFO  [com.itmo.jmx.JMXConfig] Registered MBean: com.itmo:type=AreaCalculator
```

如果看不到这两条日志，检查：
- `JMXConfig.java` 是否在 `web.xml` 的扫描路径内（`@WebListener` 注解会被 Servlet 容器自动发现）
- 应用是否正常启动

### 1.4 验证 PointsStatistics MBean

**测试目标**：确认 MBean 正确统计总点数、命中数、未命中数，并在连续 3 次未命中时发送通知。

#### 操作步骤

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| 1 | 打开应用页面 `main.xhtml` | 页面正常显示 SVG 图形区域 |
| 2 | 在 **第一象限**（右上角三角形区域，x>0, y>0）点击提交 2 个点 | 这是命中区域 |
| 3 | 在 **第四象限**（右下角矩形区域，x>0, y<0）点击提交 1 个点 | 这是命中区域 |
| 4 | 在 **第三象限**（左下角空白区域，x<0, y<0）点击提交 3 个点 | 这是未命中区域，触发通知 |

#### 用 JConsole 验证（快速方法）

打开 JConsole（见 2.2 节）连接到应用，在 MBean 选项卡中查看 `com.itmo:type=PointsStatistics`：

| 属性 | 预期值 | 说明 |
|------|--------|------|
| `TotalPoints` | 6 | 一共提交了 6 个点 |
| `HitPoints` | 3 | 前 3 个点命中 |
| `MissedPoints` | 3 | 后 3 个点未命中 |
| `ConsecutiveMisses` | 3（或 0） | 取决于第 3 次未命中后是否有新命中重置计数 |
| `HitRate` | 50.0 | 3/6 = 50% |

在 **"通知"（Notifications）** 选项卡中点击 **"订阅"（Subscribe）**，再重复步骤 4（连续 3 次未命中），应收到通知：

```
Пользователь совершил 3 промахов подряд (всего точек: X, промахов: Y)
```

#### 各象限对应的命中/未命中说明

回忆 `PointBean.checkHit()` 的判断逻辑（见 `PointBean.java:58-69`）：

| 象限 | x 符号 | y 符号 | 形状 | 条件 | 结果 |
|------|--------|--------|------|------|------|
| I（右上） | >= 0 | >= 0 | 直角三角形 | `x + y <= R` | **命中**（满足条件） |
| II（左上） | <= 0 | >= 0 | 四分之一圆 | `x² + y² <= R²` | **命中**（满足条件） |
| III（左下） | — | — | 无形状 | — | **未命中**（永远） |
| IV（右下） | >= 0 | <= 0 | 矩形 | `x <= R && y >= -R` | **命中**（满足条件） |

> **验证技巧**：第三象限（x<0, y<0）的任意点都一定是未命中，专门用于测试连续未命中通知。

### 1.5 验证 AreaCalculator MBean

**测试目标**：确认 MBean 能正确计算不同 R 值下的图形总面积。

#### 面积公式

```
总面积 S = S₁(三角形) + S₂(四分之一圆) + S₃(矩形)
         = R²/2 + πR²/4 + R²
         = R² × (6 + π) / 4
         ≈ R² × 2.285398
```

#### 操作步骤

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| 1 | 在应用页面选择 R=1，点击提交任意一个点 | AreaCalculator 的 `CurrentR` 变为 1.0 |
| 2 | 在 JConsole 中查看 `CurrentArea` | ≈ 2.285 |
| 3 | 在 JConsole → "操作" → 调用 `getArea(2)` | ≈ 9.142 |
| 4 | 调用 `getArea(3)` | ≈ 20.569 |
| 5 | 调用 `getArea(4)` | ≈ 36.566 |
| 6 | 查看 `FigureDescription` | 返回三个子区域的文字描述 |

#### 手动验算

| R | R² | 三角形 R²/2 | 四分之一圆 πR²/4 | 矩形 R² | 总面积 |
|---|-----|------------|------------------|---------|--------|
| 1 | 1 | 0.5 | 0.785 | 1 | **2.285** |
| 2 | 4 | 2.0 | 3.142 | 4 | **9.142** |
| 3 | 9 | 4.5 | 7.069 | 9 | **20.569** |
| 4 | 16 | 8.0 | 12.566 | 16 | **36.566** |

### 1.6 不依赖 JConsole 的代码级验证

如果暂时无法使用 JConsole，也可以在后端日志中验证。在 `ResultsBean.addPoint()` 方法中临时添加日志：

```java
System.out.println("[MBean] hit=" + point.getHit()
    + ", total=" + PointsStatistics.getInstance().getTotalPoints()
    + ", missed=" + PointsStatistics.getInstance().getMissedPoints()
    + ", consecutive=" + PointsStatistics.getInstance().getConsecutiveMisses());
```

每条点提交后观察 WildFly 控制台输出，验证计数器变化是否符合预期。

---

## 实验任务 2：使用 JConsole 进行程序监控

### 2.1 启动应用

首先确保应用已部署到 WildFly/JBoss 应用服务器并正常运行。

### 2.2 启动 JConsole

**方法一：命令行启动**
```bash
jconsole
```

**方法二：通过 JDK 目录启动**
```
%JAVA_HOME%\bin\jconsole.exe
```

### 2.3 连接到应用服务器

1. JConsole 启动后会显示 **"新建连接"（New Connection）** 对话框。
2. 选择 **"本地进程"（Local Process）** 选项卡。
3. 找到你的 WildFly/JBoss 进程（通常显示为 `org.jboss.modules.Main` 或 `jboss-modules.jar`），选中后点击 **"连接"（Connect）**。

> **注意**：如果 WildFly 没有出现在本地进程列表中，你需要启用 JMX 远程连接。在 WildFly 启动参数中添加：
> ```
> -Dcom.sun.management.jmxremote
> -Dcom.sun.management.jmxremote.port=9999
> -Dcom.sun.management.jmxremote.authenticate=false
> -Dcom.sun.management.jmxremote.ssl=false
> ```

### 2.4 读取任务 1 中所开发的 MBean 指标

1. 连接成功后，点击顶部 **"MBean"** 选项卡。
2. 在左侧树形导航中，展开 **`com.itmo`** 域（domain）。
3. 你会看到两个 MBean：
   - **`PointsStatistics`** — 点统计 MBean
   - **`AreaCalculator`** — 面积计算 MBean

#### 2.4.1 查看 PointsStatistics 指标

选中 **`com.itmo` → `PointsStatistics`**：

| 属性项 | 说明 | 截图记录点 |
|--------|------|-----------|
| `TotalPoints` | 用户设置的总点数 | ✅ |
| `MissedPoints` | 未落入指定区域的点数 | ✅ |
| `HitPoints` | 命中（落入目标区域）的点数 | ✅ |
| `ConsecutiveMisses` | 当前连续未命中次数 | ✅ |
| `HitRate` | 命中率（百分比%） | ✅ |

**测试方法**：
1. 在 `TotalPoints=0` 时截图一次（初始状态）。
2. 在应用网页中多次点击图形区域提交点（包含命中和未命中的区域）。
3. 在 JConsole 中点击 **"刷新"（Refresh）** 按钮观察数值变化。
4. 修改过的指标值截图记录。

**验证 MBean 通知**：
- 连续在**第三象限**（x<0, y<0，即图形的左下角空白区域）提交 3 个点。
- 点击 **"通知"（Notifications）** 选项卡（在 MBean 详细信息区底部）。
- 点击 **"订阅"（Subscribe）** 按钮。
- 然后再连续提交 3 个未命中的点，你应该能看到一条通知消息，内容类似：
  > `Пользователь совершил 3 промахов подряд`

#### 2.4.2 查看 AreaCalculator 指标

选中 **`com.itmo` → `AreaCalculator`**：

| 属性/操作项 | 说明 |
|-------------|------|
| `CurrentR` | 最近一次点检查所使用的 R 值 |
| `CurrentArea` | 对应当前 R 值的图形总面积 |
| `FigureDescription` | 图形组成部分的文字描述 |

**测试操作**：在 **"操作"（Operations）** 选项卡中，调用 `getArea(double r)` 方法，传入不同 R 值（如 R=1, 2, 3, 4），记录计算结果：
- R=1: S ≈ 2.2854
- R=2: S ≈ 9.1416
- R=3: S ≈ 20.5686
- R=4: S ≈ 36.5664

### 2.5 查看 JVM 信息

在 JConsole 顶部导航栏：

1. 点击 **"摘要"（Summary）** 选项卡。你会看到 JVM 关键信息：

| 监控项 | 位置 | 期望内容 |
|--------|------|---------|
| **JVM 名称** | "VM 摘要" 区域 → "名称" | 如 `OpenJDK 64-Bit Server VM 17.0.x` |
| **JVM 版本** | "VM 摘要" 区域 → "版本" | 如 `17.0.x+xx` |
| **Java 虚拟机供应商** | "VM 摘要" 区域 → "供应商" | 如 `Oracle Corporation` / `Eclipse Adoptium` |
| **构建版本号** | "VM 摘要" 区域 → "名称" 中通常包含 | 如 `17.0.6+10-LTS` |

2. 截图记录 **VM 摘要** 区域的完整信息。

### 2.6 JConsole 监控结论

在报告中需要总结：
- 所开发的 MBean 能够正确暴露和更新指标数据。
- JConsole 可以实时查看 MBean 属性，并调用 MBean 操作。
- MBean 通知机制在连续 3 次未命中时正确触发。

---

## 实验任务 3：使用 VisualVM 进行程序监控和分析

### 3.1 启动 VisualVM

**方法一：命令行**
```bash
jvisualvm
```

**方法二：通过 JDK 目录**
```
%JAVA_HOME%\bin\jvisualvm.exe
```

> **注意**：JDK 9+ 版本中 VisualVM 可能不再随 JDK 一起发布。如果 `jvisualvm` 命令不存在，请从 [https://visualvm.github.io/](https://visualvm.github.io/) 下载独立版。

### 3.2 连接到应用服务器进程

1. 在左侧 **"应用程序"（Applications）** 面板 → **"本地"（Local）** 节点下。
2. 找到 WildFly/JBoss 进程，**双击**打开。

### 3.3 记录 MBean 指标随时间变化的图表（任务 3 第 1 项）

**安装 VisualVM-MBeans 插件**（如果 MBeans 选项卡不可见）：
1. 菜单栏 → **工具（Tools）** → **插件（Plugins）**。
2. 在 **"可用插件"（Available Plugins）** 选项卡中搜索 **"VisualVM-MBeans"**。
3. 勾选并点击 **安装（Install）**。
4. 安装完成后重启 VisualVM。

**操作步骤**：

#### 步骤 1：打开 MBeans 浏览器
- 在进程选项卡中，点击 **"MBeans"** 选项卡。

#### 步骤 2：选择要监控的属性
- 在左侧树形结构中展开 **`com.itmo` → `PointsStatistics` → `Attributes`**。
- 右键点击 **`TotalPoints`** → 选择 **"开始图表绘制"（Start Charting）**。
- 同样操作对 **`MissedPoints`**、**`ConsecutiveMisses`** 重复。

#### 步骤 3：模拟交互（产生测试数据）
- 在应用网页中持续提交点（点击 SVG 图形的不同区域），交替提交命中和未命中的点。
- 特别在第三象限（x<0, y<0）提交 3 个连续的点来触发通知事件。

#### 步骤 4：停止图表并截图
- 在看到图表上的数值变化后，切换回 VisualVM。
- 在图表上右键 → **"另存为"（Save As）** 将图表导出为 PNG。
- 或者直接截图。

> **关键截图点**：
> 1. 初始状态（所有指标为 0）
> 2. 提交几个命中点后（TotalPoints 和 HitPoints 上升）
> 3. 提交未命中点后（MissedPoints 和 ConsecutiveMisses 变化）
> 4. 连续 3 次未命中后的图表（ConsecutiveMisses 重置为 0 时被记录）

### 3.4 确定 CPU 消耗百分比最高的线程（任务 3 第 2 项）

#### 方法一：使用 VisualVM 自带采样器

1. 在进程选项卡中，点击 **"采样器"（Sampler）** 选项卡。
2. 点击 **"CPU"** 按钮开始 CPU 采样。
3. 让应用运行一段时间（在网页上进行交互操作以产生负载）。
4. 点击 **"停止"（Stop）** 停止采样。
5. 查看 **"CPU 采样"** 结果表格。

观测结果中可以看到：
- 每条线程的名称
- CPU 时间（Total Time 列）
- 各方法的 Self Time 占比

6. 点击 **"线程 CPU 时间"** 表头按 CPU 消耗降序排列，**第一条记录**即为消耗最高的线程。
7. 记录线程名称（通常是如 `http-listener`、`default task` 等），截图保存。

#### 方法二：使用 Profiler

1. 点击 **"分析器"（Profiler）** 选项卡。
2. 选择 **"CPU"** 分析模式。
3. 点击 **"CPU"** 开始分析。
4. 在应用中进行交互操作。
5. 停止分析，查看 **"热点（Hot Spots）"** 视图。
6. 展开线程列表，观察每个线程的子调用 CPU 时间。
7. 截图热点列表。

> **报告中应包含**：
> - 线程名称
> - 该线程的 CPU 占用百分比
> - CPU 采样结果截图

### 3.5 VisualVM 分析结论

在报告中总结：
- VisualVM 可以实时绘制 MBean 属性图表，直观展示指标变化趋势。
- CPU 采样能够定位最消耗资源的线程，用于性能分析。

---

## 实验任务 4：定位并消除性能问题

> **前置说明**：代码中已预置了一个模拟性能缺陷。在 `PointBean.checkPoint()` 方法中（第 42 行）添加了 `Thread.sleep(200)`，模拟一次慢速 I/O 调用或外部服务阻塞。你的任务是使用 VisualVM / IDEA Profiler **定位这个缺陷的来源**，然后**修复它**，最后**对比修复前后的性能数据**。

---

### 4.1 缺陷代码位置

打开 `src/main/java/com/itmo/bean/PointBean.java`，第 40-42 行：

```java
// ===== SIMULATED DEFECT #1: 模拟慢速 I/O 或外部调用 =====
// 使用 VisualVM CPU Profiler 可以定位到这个 sleep 调用
try { Thread.sleep(200); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
```

这个 `sleep` 导致每次点检查额外阻塞 200ms，正常业务逻辑执行时间远小于 1ms，因此**响应时间会被放大数百倍**。

---

### 4.2 使用 VisualVM 定位缺陷（推荐方案）

#### 步骤 1：启动 CPU Profiler

1. 打开 VisualVM，双击连接 WildFly 进程（见 3.2 节）。
2. 点击 **"分析器"（Profiler）** 选项卡。
3. 选择 **CPU** 分析模式。
4. 点击 **"CPU"** 按钮开始录制。

#### 步骤 2：产生负载

1. 在浏览器中打开应用页面。
2. 在 SVG 图形区域**连续点击 10-15 次**提交点（建议点击第一象限的三角形区域以确保命中）。
3. 切换回 VisualVM，点击 **"停止"（Stop）** 结束录制。

#### 步骤 3：分析热点

录制结束后查看结果：

1. **"热点"（Hot Spots）** 视图中，按 Self Time 降序排列。
2. 你会看到 `java.lang.Thread.sleep()` 排在**最前面**，占用绝大部分 CPU 时间。
3. 展开调用栈，追溯到调用方 — 你会看到：
   ```
   java.lang.Thread.sleep(long)
     └── com.itmo.bean.PointBean.checkPoint()   ← 瓶颈在此
   ```
4. 这明确指向 `PointBean.java` 第 42 行。

#### 截图要点

- **修复前**：Hot Spots 视图，体现 `Thread.sleep` 是最大瓶颈
- **调用树**：展开到 `PointBean.checkPoint()` 的路径

---

### 4.3 使用 IDEA Profiler 定位缺陷（备选方案）

如果你使用 IntelliJ IDEA Ultimate：

1. 右键点击 WildFly 运行配置 → **"Run with Profiler"（以分析器运行）**。
2. 在 Profiler 工具窗口中选择 **CPU Profiler**。
3. 点击录制按钮，在应用中连续提交 10-15 个点。
4. 停止录制，查看 **火焰图（Flame Graph）**：
   - 火焰图中 `Thread.sleep` 会是一块**很宽的横条**，鼠标悬停可见耗时
   - 点击该横条可跳转到对应的源码行

---

### 4.4 修复缺陷

删除或注释掉 `PointBean.java` 第 40-42 行：

```java
// 修复：删除以下三行即可消除 200ms 阻塞
// try { Thread.sleep(200); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
```

---

### 4.5 修复后验证

修复后重新部署，再次用 VisualVM CPU Profiler 录制（重复 4.2 的步骤），对比：

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 单次 `checkPoint()` 平均耗时 | ~200ms | < 1ms |
| Hot Spots 首位 | `Thread.sleep` | 正常业务方法（如 `PointDao.save`） |
| 页面响应感受 | 明显卡顿 | 即时响应 |

截图保存 Hot Spots 对比。

---

### 4.6 报告填写模板（可直接使用）

```
【问题描述】
应用处理每次点检查请求时响应缓慢，单次请求耗时约 200ms，用户体验卡顿。

【定位步骤】
1. 打开 VisualVM，连接到 WildFly 进程。
2. 进入 Profiler → CPU 模式，点击"CPU"开始录制。
3. 在 Web 页面连续提交 15 个点，停止录制。
4. 查看 Hot Spots 视图：java.lang.Thread.sleep 占 CPU 时间第一位。  (附截图)
5. 展开调用栈，追溯到 com.itmo.bean.PointBean.checkPoint() 方法。  (附截图)
6. 定位到源代码文件：PointBean.java，第 42 行：
   Thread.sleep(200);
   该语句每次请求阻塞线程 200ms，是导致响应缓慢的直接原因。

【解决途径】
删除 PointBean.java 第 40-42 行的 Thread.sleep(200) 调用，恢复正常的即时处理流程。

【解决后验证】
修复后重新部署，再次用 VisualVM CPU Profiler 录制：
- 修复前：单次请求 ~200ms，Thread.sleep 为热点第一名  (附截图)
- 修复后：单次请求 < 1ms，无阻塞调用          (附截图)
```

---

## 实验报告检查清单

根据 `READMD.md` 的要求，实验报告必须包含以下内容：

- [ ] 任务文本
- [ ] 所开发的 MBean 类及相关类的源代码
- [ ] JConsole 程序截图及所读取的指标
  - [ ] PointsStatistics MBean 属性值截图
  - [ ] AreaCalculator MBean 属性值截图
  - [ ] JVM 摘要信息截图（名称、版本、供应商、构建版本号）
- [ ] JConsole 监控结果结论
- [ ] VisualVM 程序截图
  - [ ] MBean 指标随时间变化的图表截图
  - [ ] CPU 采样结果截图（标识最高 CPU 线程名称）
- [ ] VisualVM 分析结果结论
- [ ] VisualVM 查找内存泄漏过程的截图
  - [ ] Monitor 选项卡的堆内存图表截图
  - [ ] Profiler 内存分析结果截图
  - [ ] Heap Dump 类实例统计截图
- [ ] 性能问题定位与解决报告
  - [ ] 问题描述
  - [ ] 解决途径描述
  - [ ] 详细发现和定位步骤（附截图）
- [ ] 实验结论

## 答辩问题参考答案（简要）

1. **监控与分析的区别**：监控（Monitoring）是持续观察系统运行状态和指标（被动/持续）；分析（Profiling）是深入诊断和定位性能瓶颈（主动/临时）。
2. **JMX（Java Management Extensions）**：JDK 内置的监控管理基础设施，通过 MBeanServer 注册 MBean 暴露管理接口。
3. **MBean（Managed Bean）**：JMX 中的被管理资源，可以是 Standard MBean（通过接口定义）、Dynamic MBean 等。架构包含：MBean 接口、MBean 实现、MBean Server、JMX 客户端（JConsole/VisualVM）。
4. **JConsole**：JDK 自带监控工具，可查看内存、线程、MBean，适合基础监控。
5. **VisualVM**：更强大的分析和性能分析工具，支持 CPU/内存 Profiling、堆转储分析、线程转储、MBean 图表化监控。
6. **远程监控**：通过 JMX Remote API（RMI），配置 `-Dcom.sun.management.jmxremote.port` 等 JVM 参数可以实现跨网络的应用监控与分析。
