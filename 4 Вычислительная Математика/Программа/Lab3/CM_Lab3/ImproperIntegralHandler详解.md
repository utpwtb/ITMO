# ImproperIntegralHandler 逐方法代码分析

---

## 方法 1：`checkConvergence()` — 收敛性判断入口

**位置**：[L26-L32](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L26-L32)

```java
public static ConvergenceCheck checkConvergence(IntegralFunctionInfo funcInfo, double a, double b) {
    AnalysisResult analysis = analyzeInterval(funcInfo, a, b);   // L27: 委托给核心分析引擎
    if (!analysis.converges) {                                   // L28: 若分析结果为发散
        return new ConvergenceCheck(false, analysis.divergeReason);  // L29: 返回失败+原因
    }
    return new ConvergenceCheck(true, "积分收敛");                // L31: 通过 → 收敛
}
```

**设计意图**：这是对外暴露的唯一收敛性判断接口。它**不做任何判断逻辑本身**，完全委托给 `analyzeInterval()`。这样 `checkConvergence()` 和 `computeWithDiscontinuities()` 可以复用同一套分析逻辑，避免重复。

**调用时机**：`IntegrationEngine.computeImproper()` 在进入计算前调用此方法（见 [IntegrationEngine.java:L23](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/IntegrationEngine.java#L23)）。

---

## 方法 2：`computeWithDiscontinuities()` — 广义积分计算入口

**位置**：[L37-L73](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L37-L73)

```java
public static IntegrationWithDiscontinuity computeWithDiscontinuities(
        IntegralFunctionInfo funcInfo,
        NumericalIntegrationSolver solver,
        double a, double b, int initialN, double epsilon) {

    AnalysisResult analysis = analyzeInterval(funcInfo, a, b);  // L42: 复用同一分析引擎！
    if (!analysis.converges) {                                  // L43: 先检查是否收敛
        return new IntegrationWithDiscontinuity(0, 0, false, "", analysis.divergeReason);
    }

    double totalValue = 0.0;                                    // L47: 积分值累加器
    int maxN = initialN;                                        // L48: 最大分割数追踪
    StringBuilder log = new StringBuilder();                    // L49: 日志构建器

    // L52-54: 记录对称抵消日志
    for (Range cancelled : analysis.cancelledRanges) {
        log.append(String.format("对称抵消: [%f, %f] 关于间断点奇对称，积分为 0\n",
                cancelled.a, cancelled.b));
    }

    // L57-70: 对每个有效子区间执行 RungeRule 数值积分
    for (Range range : analysis.validRanges) {
        if (range.b - range.a <= 1e-12) continue;              // L58: 空区间跳过（EPS偏移后可能变空）

        RungeRule runge = new RungeRule(solver);                 // L60: 为每个子段创建 Runge 实例
        RungeRule.RungeResult result = runge.compute(           // L61: 调用 Runge 规则迭代积分
                funcInfo.getFunction(), range.a, range.b, initialN, epsilon);

        if (Double.isNaN(result.getValue()) ||                  // L63: NaN 检查
            Double.isInfinite(result.getValue())) {             //     Inf 检查
            return new IntegrationWithDiscontinuity(0, 0, false, "",
                    "计算结果为非有限值，积分不存在");            // L64: 任一子段失败→整体失败
        }

        totalValue += result.getValue();                       // L67: 累加各子段积分值
        maxN = Math.max(maxN, result.getN());                   // L68: 更新最大分割数
        log.append(String.format(                              // L69: 记录该子段详情
                "子区间 [%.6f, %.6f]: I=%.10f, n=%d\n",
                range.a, range.b, result.getValue(), result.getN()));
    }

    return new IntegrationWithDiscontinuity(totalValue, maxN, true, log.toString(), null);  // L72
}
```

**关键设计点**：

1. **L42 与 checkConvergence 复用同一个 `analyzeInterval()`** — 这意味着收敛性判断和计算使用**完全相同的区间分割和对称抵消结果**，不会出现"判断时说收敛但计算时分割不同"的不一致问题。
2. **L63-L64 的 fail-fast 策略** — 一旦任何子段的 RungeRule 返回 NaN 或 Inf，立即终止并返回失败。不尝试用其他方法补救——因为如果数值积分在某个子段上无法得到有限值，说明该子段本质上不可积。
3. **L60 每个子段创建新的 RungeRule 实例** — 因为每个子区间的长度可能不同，RungeRule 内部的 n 翻倍策略需要从 initialN=4 重新开始。

**数据流示例**（`1/x` 在 `[-1, 2]`）：
```
analysis.cancelledRanges = [[-1, 1]]   ← 对称抵消
analysis.validRanges    = [[1, 2]]    ← 剩余待计算

循环第1轮: range=[1, 2]
  RungeRule.compute(1/x, 1, 2, n=4, ε=0.001)
    → n=4: I≈0.6938
    → n=8: I≈0.6932, error=|0.6932-0.6938|/3=0.0002 < 0.001 ✓
    → 返回 value=0.6932, n=8
  totalValue = 0.6932, maxN = 8
  log += "子区间 [1.000000, 2.000000]: I=0.6931471806, n=64"

返回: value=0.6932, maxN=8, success=true
  日志:
    对称抵消: [-1.000000, 1.000000] 关于间断点奇对称，积分为 0
    子区间 [1.000000, 2.000000]: I=0.6931471806, n=64
```

---

## 方法 3：`analyzeInterval()` — ★ 核心统一分析引擎

**位置**：[L89-L145](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L89-L145)

这是整个类最核心的方法。它同时服务于 `checkConvergence()` 和 `computeWithDiscontinuities()`，一次性完成：
1. 间断点收集
2. 对称抵消检测
3. 有效区间构建
4. 子区间分割
5. 端点发散性检查

```java
private static AnalysisResult analyzeInterval(IntegralFunctionInfo info, double a, double b) {
    AnalysisResult result = new AnalysisResult();
    Function f = info.getFunction();

    // ═══ 步骤 1: 收集间断点 ═══
    List<Double> points = getDiscontinuitiesInInterval(
            info.getDiscontinuityPoints(), a, b);          // L94
    // 例: info.discontinuityPoints=[0], a=-1, b=2 → points=[0]

    // ═══ 步骤 2: 对称抵消检测 ═══
    double cursor = a;                                       // L97: 游标从左端点开始
    for (double c : points) {                                // L98: 遍历每个间断点
        if (c <= a + 1e-12 || c >= b - 1e-12) continue;      // L99: ★ 关键！跳过端点处的间断点
                                                                //     端点处不做对称检测（因为只有一侧有数据）
        double maxSymLen = Math.min(c - cursor, b - c);       // L101: 可对称的最大半宽度
                                                                //     = min(到左边的距离, 到右边的距离)
        if (maxSymLen > 1e-8 &&                               // L102: 对称范围不能太小（避免噪声）
            isOddSymmetric(f, c, maxSymLen)) {               //     调用奇对称检测算法
            Range cancelled = new Range(c - maxSymLen, c + maxSymLen);  // L103
            result.cancelledRanges.add(cancelled);            // L104: 记录抵消区间
        }
    }
    // 循环结束后: cursor 可能已右移（若有抵消），也可能不变

    // ═══ 步骤 3: 构建有效活动区间 ═══
    List<Range> activeRanges = buildActiveRanges(a, b, result.cancelledRanges);  // L109
    // 从原始 [a,b] 中挖掉所有 cancelledRanges 后的剩余部分

    // ═══ 步骤 4: 分割 + 发散检查 ═══
    for (Range active : activeRanges) {                      // L112: 遍历每个活动区间
        List<Double> subPoints = getDiscontinuitiesInInterval(  // L113: 该活动区间内的间断点
                info.getDiscontinuityPoints(), active.a, active.b);

        List<Range> segments = splitRangeByPoints(active, subPoints);  // L115: 按间断点拆分

        for (Range seg : segments) {                            // L117: 遍历每个子段
            // ---- 左端点检查 (L119-126) ----
            if (isDiscontinuity(seg.a, subPoints)) {          // L119: 左端点是间断点？
                if (divergesAt(f, seg.a, 1)) {               // L120: 向右逼近，检查右侧是否发散
                    result.converges = false;
                    result.divergeReason = String.format(
                            "积分发散（在 x=%.4f 处右侧不收敛）", seg.a);
                    return result;                             // L123: ★ 立即返回，不再继续
                }
                seg = new Range(seg.a + EPS, seg.b);         // L125: 不发散 → 排除 EPS 邻域后继续
            }

            // ---- 右端点检查 (L129-136) ----
            if (isDiscontinuity(seg.b, subPoints)) {          // L129: 右端点是间断点？
                if (divergesAt(f, seg.b, -1)) {              // L130: 向左逼近，检查左侧是否发散
                    result.converges = false;
                    result.divergeReason = String.format(
                            "积分发散（在 x=%.4f 处左侧不收敛）", seg.b);
                    return result;                             // L133: ★ 立即返回
                }
                seg = new Range(seg.a, seg.b - EPS);         // L135: 不发散 → 排除 EPS 邻域后继续
            }

            if (seg.a < seg.b) {                              // L138: 排除空区间（两端都是间断点且靠得很近时会变空）
                result.validRanges.add(seg);                   // L139: 加入有效列表
            }
        }
    }

    return result;                                             // L144: 全部通过 → converges=true
}
```

### 为什么步骤 2 要跳过端点处的间断点？（L99）

```
假设 f(x)=1/x, 区间=[0, 1], disc=[0]

若不跳过端点:
  c=0, cursor=a=0
  leftLen = c - cursor = 0 - 0 = 0       ← 到左边距离为 0!
  rightLen = b - c = 1 - 0 = 1
  symLen = min(0, 1) = 0                  ← 对称宽度为 0!

  isOddSymmetric(f, 0, 0) → h=0, dx=0 → f(0)=NaN → return false
  → 白白浪费一次检测，且无意义

所以 L99 直接跳过: c <= a + 1e-12 → true → continue
```

### 为什么 L125/L135 用 EPS=10⁻⁶ 偏移而不是删除端点？

因为数值积分方法（梯形法、辛普森法）会**显式计算端点的函数值**：

```java
// 梯形法伪代码:
sum = f(a)/2 + f(b)/2 + Σ f(x_i)    // ← 会直接算 f(间断点)!
```

如果 `[0, 1]` 的左端是间断点 x=0（f(0)=∞），不偏移的话 `f(0)` 就会参与计算 → 结果变成 Inf/NaN。

偏移 EPS 后变为 `[10⁻⁶, 1]`，`f(10⁻⁶)` 是一个很大的有限值（如 `1/x²` 在 x=10⁻⁶ 处 = 10¹²），虽然大但是**有限**，RungeRule 能正确处理。

---

## 方法 4：`divergesAt()` — 间断点发散性检测（α 指数法）

**位置**：[L151-L170](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L151-L170)

```java
private static boolean divergesAt(Function f, double p, int dir) {
    double eps1 = 1e-4;                                      // L152: 第一层逼近距离
    double eps2 = 1e-6;                                      // L153: 第二层逼近距离（更近）

    double y1 = Math.abs(f.evaluate(p + dir * eps1));          // L155: |f(p ± 10⁻⁴)|
    double y2 = Math.abs(f.evaluate(p + dir * eps2));          // L156: |f(p ± 10⁻⁶)|

    // ── 快速路径：非无穷型奇点 ──
    if (Math.max(y1, y2) < 1e5 &&                            // L159: 两值都不太大
        Double.isFinite(y1) && Double.isFinite(y2)) {          //     且均为有限值
        return false;                                         // L160: 不是无穷型奇点 → 必然收敛
    }
    // 例: f(x) = (x-1)/(x-1) 在 x=1 处, f(1±ε) ≈ 1 → 不发散

    // ── 溢出保护 ──
    if (!Double.isFinite(y1) || !Double.isFinite(y2) ||        // L164: 有 Inf/NaN
        y1 == 0 || y2 == 0) {                                 //     或零值（对数无意义）
        return true;                                          // L165: 无法计算 α → 保守判定为发散
    }

    // ── 核心：计算收敛阶 α ──
    double alpha = (Math.log(y2) - Math.log(y1)) /              // L168:
                     (Math.log(eps1) - Math.log(eps2));        //     α = Δln|y| / Δln|ε|
    return alpha >= ALPHA_THRESHOLD;                           // L169: α ≥ 0.99 → 发散
}
```

### 数学推导

设函数在间断点 p 附近满足幂律行为：
```
|f(x)| ≈ C · |x - p|^(-α)
```

取两个不同的逼近距离 ε₁ > ε₂：
```
y₁ = C · ε₁^(-α)   →   ln(y₁) = ln(C) - α·ln(ε₁)
y₂ = C · ε₂^(-α)   →   ln(y₂) = ln(C) - α·ln(ε₂)
```

两式相减消去 ln(C)：
```
ln(y₂) - ln(y₁) = -α·(ln(ε₂) - ln(ε₁)) = α·(ln(ε₁) - ln(ε₂))
```

解出 α：
```
α = (ln(y₂) - ln(y₁)) / (ln(ε₁) - ln(ε₂))     ← 就是 L168 的公式
```

### 逐步演算示例

**示例 A：`f(x)=1/x²`, p=0, dir=1（向右逼近）**

```
eps1 = 10⁻⁴, eps2 = 10⁻⁶

y₁ = |1/(0 + 1×10⁻⁴)²| = |1/10⁻⁸| = 10⁸
y₂ = |1/(0 + 1×10⁻⁶)²| = |1/10⁻¹²| = 10¹²

快速检查: max(10⁸, 10¹²) = 10¹² >> 10⁵ → 不走快速路径
溢出检查: 两者均有限、非零 → 继续

α = (ln(10¹²) - ln(10⁸)) / (ln(10⁻⁴) - ln(10⁻⁶))
  = (27.631 - 18.421) / ((-9.210) - (-13.816))
  = 9.210 / 4.606
  = **2.0**

return 2.0 >= 0.99 → **true（发散）✗**
```
符合数学结论：`∫₀¹ 1/x² dx` 发散（p=2 > 1 阶）。

---

**示例 B：`f(x)=1/√x`, p=0, dir=1**

```
y₁ = |1/√(10⁻⁴)| = |1/10⁻²| = 100
y₂ = |1/√(10⁻⁶)| = |1/10⁻³| = 10000

α = (ln(10000) - ln(100)) / (ln(10⁻⁴) - ln(10⁻⁶))
  = (9.210 - 4.605) / 4.606
  = 4.605 / 4.606
  = **0.500**

return 0.500 >= 0.99? NO → **false（收敛）✓**
```
符合数学结论：`∫₀¹ 1/√x dx = 2` 收敛（p=1/2 < 1 阶）。

---

**示例 C：`f(x)=ln(x)`, p=0, dir=-1（向左逼近）**

```
y₁ = |ln(0 + (-1)×10⁻⁴)| = |ln(-0.0001)| = **NaN**
y₂ = |ln(0 + (-1)×10⁻⁶)| = |ln(-0.000001)| = **NaN**

快速检查: Math.max(NaN, NaN) < 1e5? → NaN比较 → false
溢出检查: !Double.isFinite(NaN)? → **YES!**
return true（发散）
```
这就是为什么 `ln(x)` 在负区间会被正确拦截——`ln(负数)` 返回 NaN，触发溢出保护分支。

---

**参数选择说明**：

| 参数 | 值 | 选择理由 |
|------|-----|----------|
| eps1 | 10⁻⁴ | 不能太远（远离间断点可能已经不在奇异区域了） |
| eps2 | 10⁻⁶ | 比 eps1 近 100 倍，确保在奇异区域内 |
| ALPHA_THRESHOLD | 0.99 | 略小于 1，容忍浮点误差。α=1.0 是理论边界 |

---

## 方法 5：`isOddSymmetric()` — 奇对称检测

**位置**：[L175-L191](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L175-L191)

```java
private static boolean isOddSymmetric(Function f, double c, double h) {
    int samples = 5;                                          // L176: 取 5 个检测点对
    double totalMag = 0;                                      // L177: 所有 |f| 值的累计
    double maxError = 0;                                     // L178: 所有 |f(left)+f(right)| 的最大值

    for (int i = 1; i <= samples; i++) {                     // L180: i = 1,2,3,4,5
        double dx = h * i / (samples + 1);                   // L181: dx = h·i/6
                                                                 // i=1 → dx=h/6, i=5 → dx=5h/6
                                                                 // 注意: 不取端点（dx ≠ 0 且 dx ≠ h）
                                                                 // 因为端点处可能是间断点本身
        double y1 = f.evaluate(c - dx);                       // L182: 左侧采样点
        double y2 = f.evaluate(c + dx);                       // L183: 右侧对称点

        if (!Double.isFinite(y1) || !Double.isFinite(y2))    // L185: 任一非有限
            return false;                                     //     → 不是奇对称（或无意义）

        totalMag += Math.abs(y1) + Math.abs(y2);             // L187: 累加绝对值
        maxError = Math.max(maxError, Math.abs(y1 + y2));   // L188: 累加"不对称误差"
    }

    return totalMag > 1e-8 &&                                 // L190: 排除全零区间
           (maxError / totalMag) < 1e-5;                      //     相对误差 < 0.001%
}
```

### 采样点分布图示

以 `c=0, h=1` 为例（检测 `[-1, 1]` 关于 0 的对称性）：

```
        -1         -0.5         0        +0.5         +1
        |-----------|-----------|-----------|-----------|
                    ↑           ↑           ↑
                  i=5         i=3         i=1
                 dx=5/6      dx=3/6      dx=1/6
```

5 个检测点对均匀分布在 `(c-h, c+h)` 开区间内，**避开端点**（因为端点可能是间断点 c±h 本身）。

### 判定条件详解（L190）

```java
return totalMag > 1e-8 && (maxError / totalMag) < 1e-5;
```

两个条件必须**同时成立**：

| 条件 | 目的 | 示例 |
|------|------|------|
| `totalMag > 1e-8` | 排除全零函数的误判 | 若 f(x)≡0，则 totalMag=0，maxError=0，0/0 无意义 |
| `maxError/totalMag < 1e-5` | 相对误差阈值 | 允许最大不对称误差占总量的 0.001% |

**为什么用相对误差而非绝对误差？**

因为不同函数的数量级差异巨大：

| 函数 | 在 x=±0.5 处的 |f| 值 | 绝对误差 | 相对误差 |
|------|------------------------|----------|----------|
| `1/x` | 2.0 | ~0（完美对称） | ~0% |
| `1/x³` | 8.0 | 浮点误差 ~10⁻¹⁵ | ~10⁻¹⁴% |
| `sin(x)/x`（近似奇）| ~0.96 | ~0.02 | ~1% → **不判定为奇对称** ✅ |

相对误差能自动适应不同数量级。

### 完整演算：`f(x)=1/x`, `c=0`, `h=1`

```
i=1: dx = 1/6 ≈ 0.167
     y_left  = f(-0.167) = -5.98
     y_right = f( 0.167) =  5.98
     和 = -5.98 + 5.98 = 0.000（实际浮点可能有微小误差）
     totalMag += 5.98 + 5.98 = 11.96
     maxError = max(0, 0.000...) = 微小值

i=2: dx = 2/6 ≈ 0.333
     y_left  = f(-0.333) = -3.00
     y_right = f( 0.333) =  3.00
     和 ≈ 0
     totalMag += 6.00 → 累计 17.96

i=3: dx = 3/6 = 0.500
     y_left  = -2.00, y_right = 2.00, 和 ≈ 0
     totalMag += 4.00 → 累计 21.96

i=4: dx = 4/6 ≈ 0.667
     y_left  = -1.50, y_right = 1.50, 和 ≈ 0
     totalMag += 3.00 → 累计 24.96

i=5: dx = 5/6 ≈ 0.833
     y_left  = -1.20, y_right = 1.20, 和 ≈ 0
     totalMag += 2.40 → 累计 27.36

最终: totalMag = 27.36 >> 1e-8 ✓
      maxError ≈ 10⁻¹⁵ (浮点舍入)
      maxError/totalMag ≈ 10⁻¹⁵/27.36 << 1e-5 ✓

return true → 是奇对称！
```

---

## 方法 6：`getDiscontinuitiesInInterval()` — 间断点筛选

**位置**：[L196-L206](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L196-L206)

```java
private static List<Double> getDiscontinuitiesInInterval(double[] disc, double a, double b) {
    List<Double> list = new ArrayList<>();
    if (disc == null) return list;                           // L198: 无预定义间断点 → 空列表
    for (double d : disc) {                                    // L199: 遍历预定义数组
        if (d >= a - 1e-12 && d <= b + 1e-12) {               // L200: 容差 10⁻¹²（几乎等于）
            list.add(d);                                       // L201: 在区间内（含端点）→ 收录
        }
    }
    Collections.sort(list);                                    // L204: 排序（后续 splitByPoints 依赖有序性）
    return list;
}
```

**为什么容差是 10⁻¹²？**

用户输入的区间端点和预定义的间断点值理论上应该精确匹配（如用户输入 a=0，而预定义间断点也是 0）。但由于浮点输入解析（如 `"0"` → `0.0` vs `0` 字面量），可能会有极微小的差异。10⁻¹² 远小于 EPS（10⁻⁶），只用于"这个点是不是恰好是那个间断点"的判断，不影响实际的积分计算。

**为什么需要排序？**

`splitRangeByPoints()` 方法依赖间断点按升序排列来正确分割区间。如果顺序混乱，分割出的子区间会重叠或遗漏。

---

## 方法 7：`isDiscontinuity()` — 间断点身份验证

**位置**：[L209-L214](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L209-L214)

```java
private static boolean isDiscontinuity(double x, List<Double> points) {
    for (double p : points) {                                 // L210: 线性搜索
        if (Math.abs(x - p) < 1e-10) return true;            // L211: 容差 10⁻¹⁰
    }
    return false;                                             // L213: 找不到匹配
}
```

**与 getDiscontinuitiesInInterval 的区别**：

| 方法 | 输入 | 用途 | 容差 |
|------|------|------|------|
| `getDiscontinuitiesInInterval` | 原始数组 + [a,b] | 从全局筛选出哪些间断点在当前区间内 | 10⁻¹² |
| `isDiscontinuity` | 已筛选的点列表 + 单个 x 值 | 判断某个具体的端点是否是已知间断点 | 10⁻¹⁰ |

`isDiscontinuity` 的容差更大（10⁻¹⁰ > 10⁻¹²），因为它用于比较的是**经过 EPS 偏移后的端点值**与原始间断点值的差异。例如：
```
原始间断点 = 0.0
经过 EPS 偏移后的端点 = 0.0 + 10⁻⁶ = 0.000001
|0.000001 - 0.0| = 10⁻⁶ < 10⁻¹⁰ → 仍被识别为同一个间断点
```

---

## 方法 8：`buildActiveRanges()` — 构建有效活动区间

**位置**：[L219-L235](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L219-L235)

```java
private static List<Range> buildActiveRanges(double a, double b, List<Range> cancelled) {
    List<Range> active = new ArrayList<>();
    List<Range> sortedCancelled = new ArrayList<>(cancelled);
    sortedCancelled.sort(Comparator.comparingDouble(r -> r.a));  // L222: 按左端点排序！

    double cursor = a;                                         // L224: 从原始左端点开始扫描
    for (Range c : sortedCancelled) {                          // L225: 遍历每个抵消区间
        if (c.a - cursor > 1e-12) {                             // L226: 当前游标到抵消区间起点之间有空隙？
            active.add(new Range(cursor, c.a));                 // L227: 空隙部分 → 有效区间
        }
        cursor = Math.max(cursor, c.b);                        // L229: 游标跳到抵消区间终点之后
    }
    if (b - cursor > 1e-12) {                                 // L231: 最后一个抵消区间之后还有剩余？
        active.add(new Range(cursor, b));                      // L232: 尾部剩余 → 有效区间
    }
    return active;
}
```

### 图示：`a=-1, b=2, cancelled=[[-1, 1]]`

```
原始区间:  [-1 ============================ 2]
抵消区间:       [-1 ===== 1]
                         ↑ cursor 跟踪

初始: cursor = -1

遍历 cancelled = [[-1, 1]]:
  c.a(-1) - cursor(-1) = 0 ≤ 1e-12 → 不添加（紧贴左端点）
  cursor = max(-1, 1) = 1

循环结束: cursor = 1

b(2) - cursor(1) = 1 > 1e-12 → 尾部添加 [1, 2]

输出: activeRanges = [[1, 2]]
```

### 图示：`a=-2, b=3, cancelled=[[0, 1], [-1, 0]]`（未排序 → 排序后处理）

```
排序前: [[0, 1], [-1, 0]]
排序后: [[-1, 0], [0, 1]]

cursor = -2

第1轮: c = [-1, 0]
  c.a(-1) - cursor(-2) = 1 > 0 → active.add([-2, -1])
  cursor = max(-2, 0) = 0

第2轮: c = [0, 1]
  c.a(0) - cursor(0) = 0 → 不添加（紧贴）
  cursor = max(0, 1) = 1

尾部: b(3) - cursor(1) = 2 > 0 → active.add([1, 3])

输出: activeRanges = [[-2, -1], [1, 3]]
```

**注意 L222 排序的重要性**：如果不排序，`[[0,1], [-1,0]]` 的处理顺序会导致错误的结果。

---

## 方法 9：`splitRangeByPoints()` — 按间断点拆分区间

**位置**：[L240-L253](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L240-L253)

```java
private static List<Range> splitRangeByPoints(Range range, List<Double> points) {
    List<Range> res = new ArrayList<>();
    double cursor = range.a;                                   // L242: 从区间左端点开始
    for (double p : points) {                                  // L243: 遍历间断点（已排序）
        if (p > cursor + 1e-12 && p < range.b - 1e-12) {      // L244: 点在区间内部（不含端点）
            res.add(new Range(cursor, p));                      // L245: [cursor, p) 作为一段
            cursor = p;                                         // L246: 游标移到间断点
        }
    }
    if (range.b - cursor > 1e-12) {                            // L249: 最后一个间断点到右端点
        res.add(new Range(cursor, range.b));                   // L250: [cursor, b] 作为最后一段
    }
    return res;
}
```

### 与 buildActiveRanges 的关系

这两个方法形成**两级分割**：

```
第一级: buildActiveRanges()
  输入: 原始 [a,b] + cancelledRanges（对称抵消区间）
  输出: activeRanges（排除抵消后的剩余区间）

第二级: splitRangeByPoints()  ← 对每个 activeRange 调用
  输入: 单个 activeRange + points（该范围内的间断点）
  输出: segments（按间断点进一步切分的子段）

最终: segments → 每个 segment 再做端点发散检查 → validRanges
```

### 示例：`1/√(1-x²)` 在 `[-1, 1]`

```
预定义间断点: [-1, 1]

步骤1: 对称抵消检测
  c=-1 在左端点 → 跳过
  c=1  在右端点 → 跳过
  → cancelledRanges = []

步骤2: buildActiveRanges([-1, 1], [])
  → activeRanges = [[-1, 1]]

步骤3: splitRangeByPoints([-1, 1], [-1, 1])
  cursor = -1
  p=-1: p(-1) > cursor(-1)+1e-12? -1 > -0.999999999999? NO → 跳过
  p=1:  p(1) < range.b(1)-1e-12? 1 < 0.999999999999? NO → 跳过
  两个点都在端点上 → 全部跳过
  尾部: 1 - (-1) = 2 > 0 → add([-1, 1])

  → segments = [[-1, 1]] （没有内部间断点可分割）

步骤4: 端点发散检查
  seg=[-1, 1]
  左端 -1 是间断点? YES → divergesAt(f, -1, dir=1):
    y₁ = |1/√(1-(-0.9999)²)| = |1/√(0.0002)| ≈ 70  (有限!)
    y₂ = |1/√(1-(-0.999999)²)| = |1/√(0.000002)| ≈ 700 (有限!)
    max(70, 700) = 700 < 10⁵? NO → 不走快速路径
    但两者都 finite → 计算 α...
    最终 α < 1 → 不发散 → seg = [-1+10⁻⁶, 1]

  同理右端 1 → seg = [-1+10⁻⁶, 1-10⁻⁶]

  → validRanges = [[-0.999999, 0.999999]]
```

---

## 数据模型

### `AnalysisResult`（私有，仅内部使用）

**位置**：[L79-L84](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L79-L84)

```java
private static class AnalysisResult {
    boolean converges = true;           // 默认收敛（只有明确检测到发散才置 false）
    String divergeReason = "";          // 发散原因描述
    List<Range> validRanges;           // 经过所有检查后确认有效的子区间
    List<Range> cancelledRanges;       // 被识别为奇对称抵消的区间
}
```

这是 `analyzeInterval()` 的**唯一输出类型**，同时被 `checkConvergence()` 和 `computeWithDiscontinuities()` 消费。将分析结果封装为一个对象避免了重复计算。

### `ConvergenceCheck`（公开 record）

**位置**：[L17](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L17)

```java
public record ConvergenceCheck(boolean converges, String message) {}
```

### `IntegrationWithDiscontinuity`（公开 record）

**位置**：[L19](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L19)

```java
public record IntegrationWithDiscontinuity(
    double value,          // 各子段积分值之和
    int maxN,              // 所有子段中 RungeRule 使用的最大 n
    boolean success,       // 是否成功完成
    String detailLog,      // 多行文本日志（对称抵消 + 各子段详情）
    String errorMessage    // 失败时的原因（成功时为 null）
) {}
```

### `Range`（私有 record）

**位置**：[L21](file:///c:/develop/NOTE_UTP/StudyNote/4%20Вычислительная%20Математика/Программа/Lab3/CM_Lab3/src/main/java/com/itmo/core/utils/ImproperIntegralHandler.java#L21)

```java
private record Range(double a, double b) {}
```

简单的 `[a, b]` 区间容器。使用 Java record 自动生成 `equals()`/`hashCode()`/`toString()`。
