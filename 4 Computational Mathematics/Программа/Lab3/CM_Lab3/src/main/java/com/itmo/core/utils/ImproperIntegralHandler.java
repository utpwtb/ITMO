package com.itmo.core.utils;

import com.itmo.core.functions.Function;
import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;

import java.util.ArrayList;
import java.util.List;

public class ImproperIntegralHandler {

    private static final double DELTA = 1e-10;
    private static final int SAMPLE_COUNT = 10;

    public static ConvergenceCheck checkConvergence(IntegralFunctionInfo funcInfo, double a, double b) {
        Function function = funcInfo.getFunction();
        double[] discPoints = collectDiscPointsInInterval(funcInfo.getDiscontinuityPoints(), a, b);

        List<Range> segments = splitByDiscPoints(a, b, discPoints);

        for (Range seg : segments) {
            String validity = checkSegmentValidity(function, seg.a, seg.b);
            if (validity != null) {
                return new ConvergenceCheck(false, validity);
            }
        }

        for (double discPoint : discPoints) {
            if (discPoint >= a && discPoint <= b) {
                double leftLimit = evaluateLimit(function, discPoint, -1e-10);
                double rightLimit = evaluateLimit(function, discPoint, 1e-10);

                boolean leftInfinite = Double.isInfinite(leftLimit) || Math.abs(leftLimit) > 1e15;
                boolean rightInfinite = Double.isInfinite(rightLimit) || Math.abs(rightLimit) > 1e15;

                if (!leftInfinite && !rightInfinite) continue;

                double alphaLeft = (discPoint <= a + 1e-12) ? 0.5 : determineAlpha(function, discPoint, a, -1);
                double alphaRight = (discPoint >= b - 1e-12) ? 0.5 : determineAlpha(function, discPoint, b, 1);

                if (leftInfinite && rightInfinite) {
                    if (alphaLeft >= 1 && alphaRight >= 1) {
                        return new ConvergenceCheck(false, "积分发散（间断点 x=" + discPoint + " 处两侧均不收敛）");
                    }
                } else if (leftInfinite && alphaLeft >= 1) {
                    return new ConvergenceCheck(false, "积分发散（左端间断点 x=" + discPoint + " 处不收敛）");
                } else if (rightInfinite && alphaRight >= 1) {
                    return new ConvergenceCheck(false, "积分发散（右端间断点 x=" + discPoint + " 处不收敛）");
                }
            }
        }
        return new ConvergenceCheck(true, "积分收敛");
    }

    private static String checkSegmentValidity(Function f, double segA, double segB) {
        if (segB - segA < 1e-15) return null;

        int validCount = 0;
        int totalCount = 0;
        int nanCount = 0;
        int infCount = 0;

        for (int i = 0; i <= SAMPLE_COUNT; i++) {
            double x = segA + (segB - segA) * i / SAMPLE_COUNT;
            double val = safeEval(f, x);
            totalCount++;

            if (Double.isNaN(val)) {
                nanCount++;
            } else if (Double.isInfinite(val)) {
                infCount++;
            } else {
                validCount++;
            }
        }

        if (nanCount == totalCount) {
            return "积分不存在（区间 [%.4f, %.4f] 内函数无定义）".formatted(segA, segB);
        }

        if (nanCount > totalCount / 2) {
            return "积分不存在（区间 [%.4f, %.4f] 内大部分区域函数无定义）".formatted(segA, segB);
        }

        if (validCount == 0 && infCount > 0) {
            double midX = (segA + segB) / 2.0;
            double midVal = safeEval(f, midX);
            boolean interiorInf = Double.isInfinite(midVal);

            boolean leftEdgeInf = Double.isInfinite(safeEval(f, segA + DELTA));
            boolean rightEdgeInf = Double.isInfinite(safeEval(f, segB - DELTA));

            if (interiorInf || (!leftEdgeInf && !rightEdgeInf)) {
                return "积分不存在（区间 [%.4f, %.4f] 内函数无定义）".formatted(segA, segB);
            }
        }

        return null;
    }

    private static List<Range> splitByDiscPoints(double a, double b, double[] discPoints) {
        List<Range> segments = new ArrayList<>();
        double cursor = a;
        for (double d : discPoints) {
            if (d > cursor + 1e-12 && d < b - 1e-12) {
                segments.add(new Range(cursor, d));
                cursor = d;
            }
        }
        segments.add(new Range(cursor, b));
        return segments;
    }

    public static IntegrationWithDiscontinuity computeWithDiscontinuities(
            IntegralFunctionInfo funcInfo,
            NumericalIntegrationSolver solver,
            double a, double b, int initialN, double epsilon) {

        Function function = funcInfo.getFunction();
        double[] allDiscPoints = collectDiscPointsInInterval(funcInfo.getDiscontinuityPoints(), a, b);
        StringBuilder detailLog = new StringBuilder();

        List<Range> cancelledRanges = detectSymmetricCancellations(funcInfo, a, b, allDiscPoints, detailLog);

        List<Range> computeRanges = buildComputeRanges(a, b, allDiscPoints, cancelledRanges, detailLog);

        double totalResult = 0.0;
        int maxN = initialN;

        for (Range range : computeRanges) {
            String validity = checkSegmentValidity(function, range.a, range.b);
            if (validity != null) {
                return new IntegrationWithDiscontinuity(0, 0, false, "", validity);
            }

            double effA = adjustEndpoint(range.a, allDiscPoints, +1);
            double effB = adjustEndpoint(range.b, allDiscPoints, -1);

            if (effB - effA < 1e-15) continue;

            RungeRule runge = new RungeRule(solver);
            RungeRule.RungeResult result = runge.compute(function, effA, effB, initialN, epsilon);

            if (Double.isNaN(result.getValue()) || Double.isInfinite(result.getValue())) {
                return new IntegrationWithDiscontinuity(result.getValue(), result.getN(), false,
                        "", "计算结果为非有限值，积分不存在");
            }

            totalResult += result.getValue();
            maxN = Math.max(maxN, result.getN());

            detailLog.append(String.format(
                    "子区间 [%.6f, %.6f]: I=%.10f, n=%d\n",
                    range.a, range.b, result.getValue(), result.getN()));
        }

        return new IntegrationWithDiscontinuity(totalResult, maxN, true, detailLog.toString(), null);
    }

    private static double[] collectDiscPointsInInterval(double[] discPoints, double a, double b) {
        List<Double> collected = new ArrayList<>();
        for (double d : discPoints) {
            if (d >= a - 1e-12 && d <= b + 1e-12) {
                collected.add(d);
            }
        }
        collected.sort(null);
        double[] result = new double[collected.size()];
        for (int i = 0; i < result.length; i++) result[i] = collected.get(i);
        return result;
    }

    private static List<Range> detectSymmetricCancellations(
            IntegralFunctionInfo funcInfo, double a, double b,
            double[] discPoints, StringBuilder log) {

        List<Range> cancelled = new ArrayList<>();
        double cursor = a;

        for (double disc : discPoints) {
            if (disc < cursor || disc > b) continue;

            double leftLen = disc - cursor;
            double rightLen = b - disc;
            double symLen = Math.min(leftLen, rightLen);

            if (symLen > 1e-10 && isOddSymmetricAbout(funcInfo.getFunction(), disc, symLen)) {
                double symStart = disc - symLen;
                double symEnd = disc + symLen;
                cancelled.add(new Range(symStart, symEnd));
                log.append(String.format(
                        "对称抵消: 区间 [%.6f, %.6f] 关于间断点 %.6f 奇对称，积分为 0\n",
                        symStart, symEnd, disc));
                cursor = symEnd;
            }
        }
        return cancelled;
    }

    private static boolean isOddSymmetricAbout(Function f, double discPoint, double halfWidth) {
        int checks = 5;
        double maxErr = 0;
        double totalMag = 0;
        for (int i = 1; i <= checks; i++) {
            double offset = halfWidth * i / (checks + 1);
            double xLeft = discPoint - offset;
            double xRight = discPoint + offset;
            double vLeft = safeEval(f, xLeft);
            double vRight = safeEval(f, xRight);
            if (Double.isNaN(vLeft) || Double.isNaN(vRight)) return false;
            if (Double.isInfinite(vLeft) || Double.isInfinite(vRight)) return false;
            maxErr = Math.max(maxErr, Math.abs(vLeft + vRight));
            totalMag += Math.abs(vLeft) + Math.abs(vRight);
        }
        return totalMag > 1e-15 && maxErr / totalMag * checks < 1e-6;
    }

    private static List<Range> buildComputeRanges(double a, double b,
                                                   double[] discPoints,
                                                   List<Range> cancelledRanges,
                                                   StringBuilder log) {

        List<Range> ranges = new ArrayList<>();
        double cursor = a;

        List<Range> sortedCancelled = new ArrayList<>(cancelledRanges);
        sortedCancelled.sort((r1, r2) -> Double.compare(r1.a, r2.a));

        for (Range cr : sortedCancelled) {
            if (cr.a - cursor > 1e-15) {
                ranges.add(new Range(cursor, cr.a));
            }
            cursor = Math.max(cursor, cr.b);
        }

        if (b - cursor > 1e-15) {
            ranges.add(new Range(cursor, b));
        }

        if (ranges.isEmpty() && cancelledRanges.isEmpty()) {
            ranges.add(new Range(a, b));
        }

        return ranges;
    }

    private static double adjustEndpoint(double endpoint, double[] discPoints, int sign) {
        for (double d : discPoints) {
            if (Math.abs(endpoint - d) < 1e-10) {
                return endpoint + sign * DELTA;
            }
        }
        return endpoint;
    }

    private static double evaluateLimit(Function function, double point, double delta) {
        try {
            return function.evaluate(point + delta);
        } catch (Exception e) {
            return Double.NaN;
        }
    }

    private static double determineAlpha(Function function, double discPoint, double bound, int direction) {
        boolean foundAny = false;
        for (double eps : new double[]{1e-3, 1e-5, 1e-7}) {
            double d = direction * eps;
            double x = discPoint + d;
            if ((direction == -1 && x >= bound) || (direction == 1 && x <= bound)) {
                foundAny = true;
                double fx = Math.abs(function.evaluate(x));
                if (Double.isFinite(fx) && fx > 0) return 1.0;
            }
        }
        return foundAny ? 2.0 : 1.5;
    }

    private static double safeEval(Function f, double x) {
        return f.evaluate(x);
    }

    private record Range(double a, double b) {
    }

    public record ConvergenceCheck(boolean converges, String message) {
    }

    public record IntegrationWithDiscontinuity(double value, int maxN, boolean success, String detailLog,
                                               String errorMessage) {

    }
}
