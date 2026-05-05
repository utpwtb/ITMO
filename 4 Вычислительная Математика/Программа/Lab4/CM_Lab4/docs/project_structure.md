# 项目：最小二乘法（МНК）近似

## 项目概述

本项目实现了使用最小二乘法（МНК）进行函数近似。程序支持6种类型的近似函数，计算质量指标，并在图形界面中显示结果（包括表格和图表）。

---

## 项目结构

```
CM_Lab4/
├── pom.xml                                    # Maven配置（Java 17, UTF-8）
├── docs/
│   └── project_structure.md                   # 本文档文件
├── src/main/java/org/example/
│   ├── Main.java                              # 应用程序入口点
│   ├── engine/
│   │   └── LSMSolver.java                     # 最小二乘法数值方法
│   ├── service/
│   │   └── ApproximationService.java          # 非数值信息（消息、公式、编排）
│   ├── model/
│   │   └── ApproximationResult.java           # 近似结果的数据模型
│   └── gui/
│       ├── MainFrame.java                     # GUI主窗口
│       └── ChartPanel.java                    # 图表绘制组件
```

---

## 模块说明

### `Main.java` — 入口点

- 设置UTF-8编码
- 配置外观（Look and Feel）
- 在Swing EDT线程中启动主窗口`MainFrame`

### `model/ApproximationResult.java` — 数据模型

存储单种函数类型的近似结果：

| 字段 | 类型 | 说明 |
|------|------|------|
| `functionType` | `String` | 函数类型名称 |
| `coefficients` | `double[]` | 近似函数的系数 |
| `s` | `double` | 偏差平方和（S = Σεᵢ²） |
| `delta` | `double` | 均方根偏差（δ = √(S/n)） |
| `r2` | `double` | 决定系数R² |
| `pearsonR` | `double` | 皮尔逊相关系数（对线性函数有意义） |
| `yPredicted` | `double[]` | 预测值 φ(xᵢ) |
| `residuals` | `double[]` | 残差 εᵢ = φ(xᵢ) - yᵢ |
| `r2Message` | `String` | 近似质量的文本评估 |

### `service/ApproximationService.java` — 编排与非数值信息

- `getR2Message(r2)` — 根据R²生成质量的文本评估
- `getFormula(result)` — 生成函数公式字符串
- `computeAll(x, y)` — 运行全部6种近似类型并添加质量评估

### `gui/MainFrame.java` — 图形界面

- 左侧面板：数据输入表格和控制按钮
- 右侧面板：结果（文本）和图表分区显示
- 支持逗号作为小数分隔符
- 在UTF-8文件中加载/保存数据

### `gui/ChartPanel.java` — 图表绘制

- 绘制坐标轴、网格、标签
- 用不同颜色显示全部6条近似曲线
- 显示原始数据点
- 图例用于识别曲线
- 正确处理未定义区域（ln(x) 要求 x ≤ 0）

---

## `engine/LSMSolver.java` 详细说明

### 类的用途

`LSMSolver` 是程序的核心，实现了最小二乘法（МНК）求解近似问题的**数值方法**。该类只包含静态方法，不存储状态。所有非数值方面（公式、消息、编排）都已提取到 `ApproximationService` 中。

### 通用工作原理

对于每种函数类型，构建**正规方程组**（线性代数方程组），通过**列主元高斯消元法**求解。

### 方法说明

---

#### `private static void computeQuality(...)`

**用途**：计算近似的数值质量指标。

**参数**：
- `result` — 存储结果的对象
- `x, y` — 原始数据点
- `phi` — 近似函数 φ(x)

**计算指标**：

1. **预测值**：`yPred[i] = φ(x[i])`
2. **残差**：`res[i] = φ(x[i]) - y[i]`
3. **偏差平方和**：`S = Σ(φ(xᵢ) - yᵢ)²`
4. **均方根偏差**：`δ = √(S / n)`
5. **决定系数**：`R² = 1 - SS_res / SS_tot`
   - SS_res = Σ(φ(xᵢ) - yᵢ)² — 残差平方和
   - SS_tot = Σ(yᵢ - ȳ)² — 总平方和
   - R² = 1：完全拟合；R² = 0：模型无法解释数据
6. **皮尔逊相关系数 r**：
   - `r = cov(x,y) / √(Var(x)·Var(y))`
   - 衡量 x 和 y 之间的线性相关程度

---

#### `public static ApproximationResult linear(List<Double> x, List<Double> y)`

**近似函数**：`y = a·x + b`

**数学基础**：

线性回归的正规方程组：
```
[ Σx²   Σx ] [a]   [ Σxy ]
[ Σx    n  ] [b] = [ Σy  ]
```

使用克莱姆法则求解：
```
det = n·Σx² - (Σx)²
a = (n·Σxy - Σx·Σy) / det
b = (Σx²·Σy - Σx·Σxy) / det
```

**系数**：`{a, b}`

---

#### `public static ApproximationResult quadratic(List<Double> x, List<Double> y)`

**近似函数**：`y = c₀ + c₁·x + c₂·x²`

**数学基础**：

正规方程组（3×3）：
```
[ n    Σx    Σx² ] [c₀]   [ Σy  ]
[ Σx  Σx²   Σx³ ] [c₁] = [ Σxy ]
[ Σx² Σx³   Σx⁴ ] [c₂]   [ Σx²y]
```

使用高斯消元法（`solveGauss`）求解。

**系数**：`{c₀, c₁, c₂}`

---

#### `public static ApproximationResult cubic(List<Double> x, List<Double> y)`

**近似函数**：`y = c₀ + c₁·x + c₂·x² + c₃·x³`

**数学基础**：

正规方程组（4×4）：
```
[ n    Σx   Σx²  Σx³ ] [c₀]   [ Σy   ]
[ Σx  Σx²  Σx³  Σx⁴ ] [c₁] = [ Σxy  ]
[ Σx² Σx³  Σx⁴  Σx⁵ ] [c₂]   [ Σx²y ]
[ Σx³ Σx⁴  Σx⁵  Σx⁶ ] [c₃]   [ Σx³y ]
```

使用高斯消元法（`solveGauss`）求解。

**系数**：`{c₀, c₁, c₂, c₃}`

---

#### `public static ApproximationResult exponential(List<Double> x, List<Double> y)`

**近似函数**：`y = a·e^(b·x)`

**线性化方法**：

1. 两边取对数：`ln(y) = ln(a) + b·x`
2. 代入替换：`Y = ln(y)`，`A = b`，`B = ln(a)`
3. 得到线性问题：`Y = A·x + B`
4. 调用 `linear(x, ln(y))` 获取 A 和 B
5. 还原系数：`a = exp(B)`，`b = A`

**限制**：如果任意 yᵢ ≤ 0，自然对数未定义 — 返回 `S = Double.MAX_VALUE` 并显示错误消息。

**系数**：`{a, b}`

---

#### `public static ApproximationResult logarithmic(List<Double> x, List<Double> y)`

**近似函数**：`y = a·ln(x) + b`

**线性化方法**：

1. 代入替换 `X = ln(x)`
2. 得到线性问题：`y = a·X + b`
3. 调用 `linear(ln(x), y)` 获取 a 和 b

**限制**：如果任意 xᵢ ≤ 0，自然对数未定义 — 返回错误。

**系数**：`{a, b}`

---

#### `public static ApproximationResult power(List<Double> x, List<Double> y)`

**近似函数**：`y = a·x^b`

**线性化方法**：

1. 两边取对数：`ln(y) = ln(a) + b·ln(x)`
2. 代入替换：`X = ln(x)`，`Y = ln(y)`，`A = b`，`B = ln(a)`
3. 得到线性问题：`Y = A·X + B`
4. 调用 `linear(ln(x), ln(y))` 获取 A 和 B
5. 还原系数：`a = exp(B)`，`b = A`

**限制**：如果任意 xᵢ ≤ 0 或 yᵢ ≤ 0 — 返回错误。

**系数**：`{a, b}`

---

#### `private static double[] solveGauss(double[][] A, double[] B, int n)`

**用途**：使用列主元高斯消元法求解线性方程组 `A·x = B`。

**算法**：

1. **构建增广矩阵** `[A|B]`，大小为 n×(n+1)
2. **正向消元**（对每个列 k）：
   - 选择主元：在 `max` 行找到最大 |a[i][k]| (i ≥ k)
   - 交换第 k 行和第 max 行
   - 对所有 `i > k` 的行：计算乘数 `factor = a[i][k] / a[k][k]`，从第 i 行减去 `factor × (第 k 行)`
3. **回代**（从 n-1 到 0）：
   - `x[i] = (a[i][n] - Σⱼ₌ᵢ₊₁ⁿ⁻¹ a[i][j]·x[j]) / a[i][i]`

**数值稳定性**：列主元选择防止除以小数值，提高了求解的稳定性。

---

### 方法汇总表

| 方法 | 函数 | SLAE大小 | 线性化 |
|------|------|----------|--------|
| `linear` | y = a·x + b | 2×2（解析解） | — |
| `quadratic` | y = c₀ + c₁·x + c₂·x² | 3×3（高斯消元） | — |
| `cubic` | y = c₀ + c₁·x + c₂·x² + c₃·x³ | 4×4（高斯消元） | — |
| `exponential` | y = a·e^(b·x) | — | ln(y) = ln(a) + b·x |
| `logarithmic` | y = a·ln(x) + b | — | y = a·X + b, X = ln(x) |
| `power` | y = a·x^b | — | ln(y) = ln(a) + b·ln(x) |

---

## 编译和运行

```bash
# 编译
mvn compile

# 运行GUI
mvn exec:java -Dexec.mainClass="org.example.Main" -Dfile.encoding=UTF-8
```