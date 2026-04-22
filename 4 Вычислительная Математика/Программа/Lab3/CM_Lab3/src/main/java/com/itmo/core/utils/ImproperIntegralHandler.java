package com.itmo.core.utils;

import com.itmo.core.functions.Function;
import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;
import com.itmo.core.utils.models.AnalysisResult;
import com.itmo.core.utils.models.ConvergenceCheck;
import com.itmo.core.utils.models.IntegrationWithDiscontinuity;
import com.itmo.core.utils.models.Range;
import com.itmo.core.utils.models.RungeResult;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class ImproperIntegralHandler {

    private static final double EPS = 1e-6; // 排除间断点邻域的偏移量
    private static final double ALPHA_THRESHOLD = 0.99; // 判断发散的阶数阈值

    /**
     * 收敛性判断入口
     */
    public static ConvergenceCheck checkConvergence(IntegralFunctionInfo funcInfo, double a, double b) {
        AnalysisResult analysis = analyzeInterval(funcInfo, a, b);
        if (!analysis.converges) {
            return new ConvergenceCheck(false, analysis.divergeReason);
        }
        return new ConvergenceCheck(true, "Интеграл сходится");
    }

    /**
     * 带间断点处理的数值积分计算
     */
    public static IntegrationWithDiscontinuity computeWithDiscontinuities(
            IntegralFunctionInfo funcInfo,
            NumericalIntegrationSolver solver,
            double a, double b, int initialN, double epsilon) {

        AnalysisResult analysis = analyzeInterval(funcInfo, a, b);
        if (!analysis.converges) {
            return new IntegrationWithDiscontinuity(0, 0, false, "", analysis.divergeReason);
        }

        double totalValue = 0.0;
        int maxN = initialN;
        StringBuilder log = new StringBuilder();

        // 对称抵消日志
        for (Range cancelled : analysis.cancelledRanges) {
            log.append(String.format("Симметричная компенсация: [%f, %f] - нечётная симметрия относительно точки разрыва, интеграл = 0\n", cancelled.a, cancelled.b));
        }

        // 对剩余有效子区间逐段积分
        for (Range range : analysis.validRanges) {
            if (range.b - range.a <= 1e-12) continue;

            RungeRule runge = new RungeRule(solver);
            RungeResult result = runge.compute(funcInfo.getFunction(), range.a, range.b, initialN, epsilon);

            if (Double.isNaN(result.getValue()) || Double.isInfinite(result.getValue())) {
                return new IntegrationWithDiscontinuity(0, 0, false, "", "Результат вычисления не является конечным значением, интеграл не существует");
            }

            totalValue += result.getValue();
            maxN = Math.max(maxN, result.getN());
            log.append(String.format("Подинтервал [%.6f, %.6f]: I=%.10f, n=%d\n", range.a, range.b, result.getValue(), result.getN()));
        }

        return new IntegrationWithDiscontinuity(totalValue, maxN, true, log.toString(), null);
    }

    // ----------------------------------------------------
    // 内部分析逻辑
    // ----------------------------------------------------

    /**
     * 核心分析方法：对整个区间进行收敛性判断 + 区间分割
     */
    private static AnalysisResult analyzeInterval(IntegralFunctionInfo info, double a, double b) {
        AnalysisResult result = new AnalysisResult();
        Function f = info.getFunction();

        // 1. 收集区间内所有间断点（排序+去重）
        List<Double> points = getDiscontinuitiesInInterval(info.getDiscontinuityPoints(), a, b);

        // 2. 检测对称抵消（仅处理内部间断点）
        double cursor = a;
        for (double c : points) {
            if (c <= a + 1e-12 || c >= b - 1e-12) continue; // 跳过端点处的间断点

            double maxSymLen = Math.min(c - cursor, b - c);
            if (maxSymLen > 1e-8 && isOddSymmetric(f, c, maxSymLen)) {
                Range cancelled = new Range(c - maxSymLen, c + maxSymLen);
                result.cancelledRanges.add(cancelled);
            }
        }

        // 3. 构建有效活动区间（排除已抵消的部分）
        List<Range> activeRanges = buildActiveRanges(a, b, result.cancelledRanges);

        // 4. 按间断点进一步分割 + 端点发散性检查
        for (Range active : activeRanges) {
            List<Double> subPoints = getDiscontinuitiesInInterval(info.getDiscontinuityPoints(), active.a, active.b);

            List<Range> segments = splitRangeByPoints(active, subPoints);

            for (Range seg : segments) {
                // 左端点是间断点 → 检查右侧是否发散
                if (isDiscontinuity(seg.a, subPoints)) {
                    if (divergesAt(f, seg.a, 1)) {
                        result.converges = false;
                        result.divergeReason = String.format("Интеграл расходится (справа от x=%.4f не сходится)", seg.a);
                        return result;
                    }
                    seg = new Range(seg.a + EPS, seg.b); // 排除 ε 邻域
                }

                // 右端点是间断点 → 检查左侧是否发散
                if (isDiscontinuity(seg.b, subPoints)) {
                    if (divergesAt(f, seg.b, -1)) {
                        result.converges = false;
                        result.divergeReason = String.format("Интеграл расходится (слева от x=%.4f не сходится)", seg.b);
                        return result;
                    }
                    seg = new Range(seg.a, seg.b - EPS); // 排除 ε 邻域
                }

                if (seg.a < seg.b) {
                    result.validRanges.add(seg);
                }
            }
        }

        return result;
    }

    /**
     * 判断在间断点 p 的 dir 方向上积分是否发散
     * dir=1 表示向右（右侧逼近），dir=-1 表示向左（左侧逼近）
     */
    private static boolean divergesAt(Function f, double p, int dir) {
        double eps1 = 1e-4;
        double eps2 = 1e-6;

        double y1 = Math.abs(f.evaluate(p + dir * eps1));
        double y2 = Math.abs(f.evaluate(p + dir * eps2));

        // 若附近值不趋向无穷（可去/跳跃），则收敛
        if (Math.max(y1, y2) < 1e5 && Double.isFinite(y1) && Double.isFinite(y2)) {
            return false;
        }

        // 计算收敛阶数 alpha: f(x) ~ 1/x^alpha
        if (!Double.isFinite(y1) || !Double.isFinite(y2) || y1 == 0 || y2 == 0) {
            return true; // 溢出 → 发散
        }

        double alpha = (Math.log(y2) - Math.log(y1)) / (Math.log(eps1) - Math.log(eps2));
        return alpha >= ALPHA_THRESHOLD;
    }

    /**
     * 判断函数 f 在点 c 的半径 h 范围内是否关于 c 奇对称: f(c-x) + f(c+x) ≈ 0
     */
    private static boolean isOddSymmetric(Function f, double c, double h) {
        int samples = 5;
        double totalMag = 0;
        double maxError = 0;

        for (int i = 1; i <= samples; i++) {
            double dx = h * i / (samples + 1);
            double y1 = f.evaluate(c - dx);
            double y2 = f.evaluate(c + dx);

            if (!Double.isFinite(y1) || !Double.isFinite(y2)) return false;

            totalMag += Math.abs(y1) + Math.abs(y2);
            maxError = Math.max(maxError, Math.abs(y1 + y2));
        }
        return totalMag > 1e-8 && (maxError / totalMag) < 1e-5;
    }

    /**
     * 从预定义的间断点数组中筛选出落在 [a, b] 区间内的点
     */
    private static List<Double> getDiscontinuitiesInInterval(double[] disc, double a, double b) {
        List<Double> list = new ArrayList<>();
        if (disc == null) return list;
        for (double d : disc) {
            if (d >= a - 1e-12 && d <= b + 1e-12) {
                list.add(d);
            }
        }
        Collections.sort(list);
        return list;
    }

    /** 判断 x 是否是已知间断点 */
    private static boolean isDiscontinuity(double x, List<Double> points) {
        for (double p : points) {
            if (Math.abs(x - p) < 1e-10) return true;
        }
        return false;
    }

    /**
     * 从 [a, b] 中排除已标记为对称抵消的区间，构建剩余有效区间列表
     */
    private static List<Range> buildActiveRanges(double a, double b, List<Range> cancelled) {
        List<Range> active = new ArrayList<>();
        List<Range> sortedCancelled = new ArrayList<>(cancelled);
        sortedCancelled.sort(Comparator.comparingDouble(r -> r.a));

        double cursor = a;
        for (Range c : sortedCancelled) {
            if (c.a - cursor > 1e-12) {
                active.add(new Range(cursor, c.a));
            }
            cursor = Math.max(cursor, c.b);
        }
        if (b - cursor > 1e-12) {
            active.add(new Range(cursor, b));
        }
        return active;
    }

    /**
     * 按间断点将一个区间拆分为多个子段
     */
    private static List<Range> splitRangeByPoints(Range range, List<Double> points) {
        List<Range> res = new ArrayList<>();
        double cursor = range.a;
        for (double p : points) {
            if (p > cursor + 1e-12 && p < range.b - 1e-12) {
                res.add(new Range(cursor, p));
                cursor = p;
            }
        }
        if (range.b - cursor > 1e-12) {
            res.add(new Range(cursor, range.b));
        }
        return res;
    }
}
