# 数值积分计算程序 (Lab3) — 项目结构与核心组件详解

## 一、项目结构总览

```
CM_Lab3/
├── pom.xml                          # Maven 项目配置，依赖 Lombok
├── desc_lab.md                      # 实验要求文档
├── py/                              # Python 参考实现
│   ├── main.py                      # 主程序（函数列表 + 积分计算）
│   └── MidpointTrapezoidSimpson.py  # 符号计算验证脚本
└── src/main/java/com/itmo/
    ├── Main.java                    # 程序入口，交互循环
    └── core/
        ├── functions/               # 函数定义层
        │   ├── Function.java                    # 函数接口 (evaluate)
        │   ├── IntegralFunctionInfo.java        # 函数元信息（名称/间断点/默认区间）
        │   └── IntegralRepository.java          # 10 个内置函数实现
        ├── solvers/integration/     # 数值积分算法层（策略模式）
        │   ├── NumericalIntegrationSolver.java  # 积分器接口
        │   ├── LeftRectangleSolver.java          # 左矩形法
        │   ├── RightRectangleSolver.java         # 右矩形法
        │   ├── MidpointRectangleSolver.java      # 中矩形法
        │   ├── TrapezoidalSolver.java            # 梯形法
        │   └── SimpsonSolver.java                # 辛普森法
        ├── model/
        │   └── IntegrationResult.java            # 通用积分结果模型
        └── utils/                      # 核心工具层
            ├── InputHandler.java              # 用户输入处理
            ├── ResultFormatter.java            # 输出格式化
            ├── RungeRule.java                  # Runge 收敛判断
            ├── IntegrationEngine.java          # 计算流程编排
            └── ImproperIntegralHandler.java     # 广义积分处理（核心）
```

### 分层架构说明

```
┌─────────────────────────────────────────┐
│              Main.java                   │  ← 入口与交互循环
├─────────────────────────────────────────┤
│           InputHandler / ResultFormatter │  ← 输入/输出（分离关注点）
├─────────────────────────────────────────┤
│           IntegrationEngine              │  ← 流程编排（判断类型 → 分派）
├─────────────────────────────────────────┤
│  RungeRule    │   ImproperIntegralHandler│  ← 核心算法
│  (收敛判断)   │   (广义积分/间断点处理)    │
├─────────────────────────────────────────┤
│   NumericalIntegrationSolver (策略模式)   │  ← 5 种数值积分算法
│  左矩形 | 右矩形 | 中矩形 | 梯形 | 辛普森 │
├─────────────────────────────────────────┤
│        Function / IntegralFunctionInfo   │  ← 函数抽象与元数据
└─────────────────────────────────────────┘
```

---

## 二、ImproperIntegralHandler 详解

### 2.1 职责概述

`ImproperIntegralHandler` 专门处理**第二类广义积分**（函数在区间内存在**无穷间断点**），如：

- `1/x` 在 `x=0` 处无定义（间断点）
- `ln(x)` 在 `x≤0` 处无定义（定义域外）
- `1/sqrt(x)` 在 `x=0` 处趋向无穷

**核心职责**：
1. **收敛性判断** — 在计算前判断积分是否收敛
2. **子区间分割** — 按间断点将区间拆分为若干子段
3. **对称抵消检测** — 识别跨间断点的奇对称区间并标记为相互抵消
4. **逐段数值积分** — 对每个有效子段执行带 Runge 规则的数值积分

### 2.2 关键常量

```java
private static final double DELTA = 1e-10;        // 端点偏移量（避免在间断点处求值）
private static final int SAMPLE_COUNT = 10;       // 区间有效性检测采样点数
```

### 2.3 公开 API

#### `checkConvergence()` — 收敛性判断

入口方法，输入函数信息 `[a, b]`，返回 `ConvergenceCheck`（是否收敛 + 消息）。

**执行流程**：

```
checkConvergence(funcInfo, a, b)
│
├─ 1. 收集区间内间断点
│
├─ 2. splitByDiscPoints() 将 [a,b] 按间断点分割
│   例: [a, disc1, disc2, b] → [a, disc1], [disc1, disc2], [disc2, b]
│
├─ 3. 对每个子段调用 checkSegmentValidity()
│   ├─ 采样 SAMPLE_COUNT+1 个点
│   ├─ 若全部 NaN → "积分不存在"
│   └─ 若大部分 NaN → "大部分无定义"
│
├─ 4. 逐个间断点分析收敛性（仅对无穷间断点）
│   ├─ 两侧均有限 → 跳过（不是广义积分）
│   ├─ 两侧均无穷 → 两侧 α 均 < 1 才收敛
│   ├─ 仅左侧无穷 → α_left < 1 才收敛
│   └─ 仅右侧无穷 → α_right < 1 才收敛
│
└─ 5. 全部通过 → converges=true
```

#### `computeWithDiscontinuities()` — 广义积分计算

返回 `IntegrationWithDiscontinuity`（积分值、最大分割数、是否成功、详细日志）。

**执行流程**：

```
computeWithDiscontinuities(funcInfo, solver, a, b, initialN, epsilon)
│
├─ 1. collectDiscPointsInInterval()       // 收集区间内间断点
│
├─ 2. detectSymmetricCancellations()      // 检测跨间断点对称抵消
│   例: 1/x 在 [-1, 2] 中，[-1, 0] 和 [0, 1] 关于 x=0 奇对称
│       → 抵消，cursor 移动到 1
│
├─ 3. buildComputeRanges()                // 构建待计算区间列表
│   例: [-1, 2], disc=0, cancelled=[-1,1]
│       → computeRanges = [1, 2]（只剩右侧）
│
├─ 4. 遍历 computeRanges，对每段：
│   ├─ checkSegmentValidity()             // 二次验证函数在子段有定义
│   ├─ adjustEndpoint()                   // 端点若为间断点则偏移 DELTA
│   ├─ RungeRule.compute()                // 带 Runge 规则的数值积分
│   └─ NaN/Inf 检查 → 失败立即返回
│
└─ 5. 返回 IntegrationWithDiscontinuity
```

### 2.4 核心内部方法

#### `splitByDiscPoints()` — 按间断点分割区间

```java
输入: a=-1, b=2, discPoints=[0]
输出: [[-1, 0], [0, 2]]

若 disc=0 在区间内部（a < disc < b），则：
  [-1, 0]   ← 左子段（cursor 停在 0）
  [0, 2]    ← 右子段（cursor 从 0 开始）
```

#### `checkSegmentValidity()` — 区间有效性检验

防止函数在子区间内**大部分无定义**（如 `ln(x)` 在 `[-1, 0]` 整体无定义）的情况被漏判。

```
在 [segA, segB] 上均匀采样 SAMPLE_COUNT+1 个点：
  全部 NaN → "积分不存在"
  >50% NaN → "大部分无定义"
  全为 Inf 但两端非间断点 → "非标准广义积分"
  否则 → 通过
```

#### `detectSymmetricCancellations()` — 跨间断点对称抵消

以 `1/x, [-1, 2]` 为例（间断点 `x=0`）：

```
cursor = -1, 遍历 disc=0:
  leftLen  = 0 - (-1) = 1      // cursor 到间断点的距离
  rightLen = 2 - 0 = 2         // 间断点到区间右端的距离
  symLen   = min(1, 2) = 1     // 可对称的最大半宽度

  检测 isOddSymmetricAbout(f, disc=0, halfWidth=1):
    取 5 个检测点: x = -0.9, -0.8, -0.7, -0.6, -0.5
    验证 f(-xi) ≈ -f(xi) 对所有 i 成立

  若对称:
    cancelled.add([-1.0, 1.0])
    cursor = 1.0

  → 剩余待计算区间: [1.0, 2.0]
```

**关键判断逻辑**：`isOddSymmetricAbout()`
- 在 `[disc - halfWidth, disc + halfWidth]` 内取 5 个对称点对
- 验证 `f(x_left) + f(x_right) ≈ 0`（相对误差 < 1e-6）
- 相对误差 = `maxErr / totalMag × checks`，其中 `totalMag > 1e-15` 确保分母不为零

#### `adjustEndpoint()` — 端点极限逼近

当子区间端点恰好是间断点时，数值方法（如梯形法/辛普森法）会直接计算 `f(间断点)` → `NaN`。

```
例: 子区间 [0, 2], disc=0
  effA = adjustEndpoint(0, [0], +1) → 0 + 1e-10 = 1e-10   ← 避免在 0 处求值
  effB = adjustEndpoint(2, [0], -1) → 2                   ← 正常

  实际计算区间: [1e-10, 2]
```

#### `determineAlpha()` — 收敛指数判定

用于判断无穷间断点处的收敛速度。对接近间断点的点列采样：

```java
direction = -1（左侧逼近）: x = discPoint - eps, eps ∈ {1e-3, 1e-5, 1e-7}
direction = +1（右侧逼近）: x = discPoint + eps, eps ∈ {1e-3, 1e-5, 1e-7}

判断: |f(x)| 在 ε→0 时是否趋向无穷？
  → 有界（finite 且 > 0）→ α = 1.0（边界情况）
  → 无法确定 → α = 0.5（保守，视为收敛）
```

### 2.5 数据模型

#### `ConvergenceCheck`

```java
public ConvergenceCheck(boolean converges, String message)
// converges=true  → 可继续计算
// converges=false → 输出 message，积分不存在
```

#### `IntegrationWithDiscontinuity`

```java
public IntegrationWithDiscontinuity(
    double value,          // 积分值
    int maxN,              // 最大分割数
    boolean success,       // 是否成功
    String detailLog,      // 各子段计算详情（换行分隔）
    String errorMessage    // 失败时的错误描述
)
```

### 2.6 与 Python 实现的差异

| 方面 | Python (`main.py`) | Java (`ImproperIntegralHandler`) |
|------|--------------------|-----------------------------------|
| 间断点检测 | 运行时动态采样 + 异常捕获 | 预定义在 `IntegralRepository` 中 |
| 收敛性判断 | 检查 `|y1 - y2| > eps` 简单差值 | α 指数分析，更严谨 |
| 对称抵消 | **无** | **有**，跨间断点检测奇函数特征 |
| 区间有效性 | **无**，`ln(x)` 负区间会算出 `-Infinity` | 采样验证，防止无定义区间 |
| 端点处理 | `a += eps` 或 `b -= eps`（整个端点） | `adjustEndpoint` 精确到间断点 |

---

## 三、Runge 规则与精度阶

数值积分方法的精度由**截断误差的主项阶数**决定，Runge 规则利用这一特性进行误差估计。

### 误差估计公式

```
R ≈ (I_{2n} - I_n) / (2^p - 1)

其中:
  I_n    = 分割数为 n 时的积分近似值
  I_{2n} = 分割数加倍后的积分近似值
  p      = 方法的精度阶数
  2^p-1  = Runge 系数
```

### 各方法精度阶数

| 方法 | 精度阶 p | Runge 系数 (2^p - 1) | Java `order` |
|------|:---:|:---:|:---:|
| 左矩形法 | 1 | **1** | 1 |
| 右矩形法 | 1 | **1** | 1 |
| 中矩形法 | 2 | **3** | 2 |
| 梯形法 | 2 | **3** | 2 |
| 辛普森法 | 4 | **15** | 4 |

### 收敛判断流程（`RungeRule.compute`）

```
初始 n = 4
prev = solver.integrate(f, a, b, n)

while error > epsilon && iterations < 10000:
    n *= 2
    curr = solver.integrate(f, a, b, n)
    error = |curr - prev| / (2^order - 1)
    if error <= epsilon: return curr (converged)
    prev = curr

return curr (可能未收敛)
```

---

## 四、数据流总览

以计算 `∫[0,2] 1/x dx` 为例（广义积分，间断点 x=0）：

```
用户输入: f=1/x, a=-1, b=2, epsilon=0.001, method=midpoint

Main
 └─ IntegrationEngine.computeImproper()
     │
     ├─ ImproperIntegralHandler.checkConvergence()
     │   ├─ splitByDiscPoints: [-1,0], [0,2]
     │   ├─ checkSegmentValidity: 全部有效（有对称抵消兜底）
     │   ├─ disc=0: 两侧无穷, α_left<1, α_right<1 → 收敛
     │   └─ return ConvergenceCheck(true, "积分收敛")
     │
     └─ ImproperIntegralHandler.computeWithDiscontinuities()
         ├─ collectDiscPoints: [0]
         ├─ detectSymmetricCancellations():
         │   leftLen=1, rightLen=2, symLen=1
         │   isOddSymmetricAbout(f, 0, 1) → true（1/x 是奇函数）
         │   → cancelled = [[-1, 1]], cursor = 1
         ├─ buildComputeRanges: [[1, 2]]
         │
         └─ 遍历 [[1, 2]]:
              ├─ checkSegmentValidity: 通过
              ├─ adjustEndpoint: [1e-10, 2]
              ├─ RungeRule.compute(f, 1e-10, 2, n=4, eps=0.001)
              │   → n 逐步加倍直到误差 < eps
              │   → I = ln(2) ≈ 0.693147...
              └─ detailLog: "子区间 [1.000000, 2.000000]: I=0.6931471806, n=64"

ResultFormatter 输出:
  【中矩形法 - 广义积分计算】
    积分值: 0.6931471806
    最大分割数: n = 64
    计算详情:
      对称抵消: 区间 [-1.000000, 1.000000] 关于间断点 0.000000 奇对称，积分为 0
      子区间 [1.000000, 2.000000]: I=0.6931471806, n=64
```
