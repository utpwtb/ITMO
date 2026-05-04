package org.example.engine;

import org.example.model.ApproximationResult;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class LSMSolver {

    private static void computeQuality(ApproximationResult result, List<Double> x, List<Double> y,
                                       Function<Double, Double> phi) {
        int n = x.size();
        double s = 0;
        double meanY = y.stream().mapToDouble(Double::doubleValue).average().orElse(0);

        double[] yPred = new double[n];
        double[] res = new double[n];

        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yi = y.get(i);
            double pi = phi.apply(x.get(i));
            yPred[i] = pi;
            double eps = pi - yi;
            res[i] = eps;
            ssRes += eps * eps;
            ssTot += (yi - meanY) * (yi - meanY);
        }

        result.setS(ssRes);
        result.setDelta(Math.sqrt(ssRes / n));
        result.setYPredicted(yPred);
        result.setResiduals(res);

        double r2 = ssTot == 0 ? 1.0 : 1 - ssRes / ssTot;
        result.setR2(r2);

        String msg;
        if (r2 >= 0.95) msg = "高精度逼近 (R^2 >= 0.95)";
        else if (r2 >= 0.75) msg = "满意的逼近 (0.75 <= R^2 < 0.95)";
        else if (r2 >= 0.5) msg = "弱逼近 (0.5 <= R^2 < 0.75)";
        else msg = "逼近精度不足 (R^2 < 0.5)";
        result.setR2Message(msg);

        // Pearson correlation for linear
        double meanX = x.stream().mapToDouble(Double::doubleValue).average().orElse(0);
        double cov = 0, varX = 0, varY = 0;
        for (int i = 0; i < n; i++) {
            cov += (x.get(i) - meanX) * (y.get(i) - meanY);
            varX += (x.get(i) - meanX) * (x.get(i) - meanX);
            varY += (y.get(i) - meanY) * (y.get(i) - meanY);
        }
        double denom = Math.sqrt(varX * varY);
        result.setPearsonR(denom == 0 ? 0 : cov / denom);
    }

    public static ApproximationResult linear(List<Double> x, List<Double> y) {
        int n = x.size();
        double sX = 0, sXX = 0, sY = 0, sXY = 0;
        for (int i = 0; i < n; i++) {
            double xi = x.get(i), yi = y.get(i);
            sX += xi; sXX += xi * xi; sY += yi; sXY += xi * yi;
        }
        double det = sXX * n - sX * sX;
        double a = (sXY * n - sX * sY) / det;
        double b = (sXX * sY - sX * sXY) / det;

        ApproximationResult result = new ApproximationResult("线性函数", new double[]{a, b});
        computeQuality(result, x, y, xi -> a * xi + b);
        return result;
    }

    public static ApproximationResult quadratic(List<Double> x, List<Double> y) {
        int n = x.size();
        double sX = 0, sX2 = 0, sX3 = 0, sX4 = 0, sY = 0, sXY = 0, sX2Y = 0;
        for (int i = 0; i < n; i++) {
            double xi = x.get(i), yi = y.get(i);
            double x2 = xi * xi;
            sX += xi; sX2 += x2; sX3 += x2 * xi; sX4 += x2 * x2;
            sY += yi; sXY += xi * yi; sX2Y += x2 * yi;
        }
        double[][] A = {{n, sX, sX2}, {sX, sX2, sX3}, {sX2, sX3, sX4}};
        double[] B = {sY, sXY, sX2Y};
        double[] coeffs = solveGauss(A, B, 3);

        ApproximationResult result = new ApproximationResult("二次多项式", coeffs);
        computeQuality(result, x, y, xi -> coeffs[0] + coeffs[1] * xi + coeffs[2] * xi * xi);
        return result;
    }

    public static ApproximationResult cubic(List<Double> x, List<Double> y) {
        int n = x.size();
        double sX = 0, sX2 = 0, sX3 = 0, sX4 = 0, sX5 = 0, sX6 = 0;
        double sY = 0, sXY = 0, sX2Y = 0, sX3Y = 0;
        for (int i = 0; i < n; i++) {
            double xi = x.get(i), yi = y.get(i);
            double x2 = xi * xi, x3 = x2 * xi;
            sX += xi; sX2 += x2; sX3 += x3; sX4 += x2 * x2; sX5 += x3 * x2; sX6 += x3 * x3;
            sY += yi; sXY += xi * yi; sX2Y += x2 * yi; sX3Y += x3 * yi;
        }
        double[][] A = {
                {n, sX, sX2, sX3},
                {sX, sX2, sX3, sX4},
                {sX2, sX3, sX4, sX5},
                {sX3, sX4, sX5, sX6}
        };
        double[] B = {sY, sXY, sX2Y, sX3Y};
        double[] coeffs = solveGauss(A, B, 4);

        ApproximationResult result = new ApproximationResult("三次多项式", coeffs);
        computeQuality(result, x, y, xi -> coeffs[0] + coeffs[1] * xi + coeffs[2] * xi * xi + coeffs[3] * xi * xi * xi);
        return result;
    }

    public static ApproximationResult exponential(List<Double> x, List<Double> y) {
        List<Double> lnY = y.stream().map(v -> {
            if (v <= 0) return Double.NaN;
            return Math.log(v);
        }).collect(Collectors.toList());

        if (lnY.contains(Double.NaN)) {
            ApproximationResult bad = new ApproximationResult("指数函数", new double[]{0, 0});
            bad.setS(Double.MAX_VALUE);
            bad.setDelta(Double.MAX_VALUE);
            bad.setR2(0);
            bad.setR2Message("数据含非正值，无法拟合指数函数");
            bad.setYPredicted(new double[x.size()]);
            bad.setResiduals(new double[x.size()]);
            return bad;
        }

        ApproximationResult lin = linear(x, lnY);
        double a = Math.exp(lin.getCoefficients()[1]); // intercept was b
        double b = lin.getCoefficients()[0];           // slope was a

        ApproximationResult result = new ApproximationResult("指数函数", new double[]{a, b});
        computeQuality(result, x, y, xi -> a * Math.exp(b * xi));
        return result;
    }

    public static ApproximationResult logarithmic(List<Double> x, List<Double> y) {
        List<Double> lnX = x.stream().map(v -> {
            if (v <= 0) return Double.NaN;
            return Math.log(v);
        }).collect(Collectors.toList());

        if (lnX.contains(Double.NaN)) {
            ApproximationResult bad = new ApproximationResult("对数函数", new double[]{0, 0});
            bad.setS(Double.MAX_VALUE);
            bad.setDelta(Double.MAX_VALUE);
            bad.setR2(0);
            bad.setR2Message("数据含非正值，无法拟合对数函数");
            bad.setYPredicted(new double[x.size()]);
            bad.setResiduals(new double[x.size()]);
            return bad;
        }

        ApproximationResult lin = linear(lnX, y);
        double a = lin.getCoefficients()[0];
        double b = lin.getCoefficients()[1];

        ApproximationResult result = new ApproximationResult("对数函数", new double[]{a, b});
        computeQuality(result, x, y, xi -> xi > 0 ? a * Math.log(xi) + b : b);
        return result;
    }

    public static ApproximationResult power(List<Double> x, List<Double> y) {
        List<Double> lnX = x.stream().map(v -> {
            if (v <= 0) return Double.NaN;
            return Math.log(v);
        }).collect(Collectors.toList());
        List<Double> lnY = y.stream().map(v -> {
            if (v <= 0) return Double.NaN;
            return Math.log(v);
        }).collect(Collectors.toList());

        if (lnX.contains(Double.NaN) || lnY.contains(Double.NaN)) {
            ApproximationResult bad = new ApproximationResult("幂函数", new double[]{0, 0});
            bad.setS(Double.MAX_VALUE);
            bad.setDelta(Double.MAX_VALUE);
            bad.setR2(0);
            bad.setR2Message("数据含非正值，无法拟合幂函数");
            bad.setYPredicted(new double[x.size()]);
            bad.setResiduals(new double[x.size()]);
            return bad;
        }

        ApproximationResult lin = linear(lnX, lnY);
        double a = Math.exp(lin.getCoefficients()[1]);
        double b = lin.getCoefficients()[0];

        ApproximationResult result = new ApproximationResult("幂函数", new double[]{a, b});
        computeQuality(result, x, y, xi -> xi > 0 ? a * Math.pow(xi, b) : 0);
        return result;
    }

    private static double[] solveGauss(double[][] A, double[] B, int n) {
        double[][] a = new double[n][n + 1];
        for (int i = 0; i < n; i++) {
            System.arraycopy(A[i], 0, a[i], 0, n);
            a[i][n] = B[i];
        }

        for (int k = 0; k < n; k++) {
            int max = k;
            for (int i = k + 1; i < n; i++) {
                if (Math.abs(a[i][k]) > Math.abs(a[max][k])) max = i;
            }
            double[] tmp = a[k]; a[k] = a[max]; a[max] = tmp;

            for (int i = k + 1; i < n; i++) {
                double factor = a[i][k] / a[k][k];
                for (int j = k; j <= n; j++) {
                    a[i][j] -= factor * a[k][j];
                }
            }
        }

        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {
            double sum = a[i][n];
            for (int j = i + 1; j < n; j++) {
                sum -= a[i][j] * x[j];
            }
            x[i] = sum / a[i][i];
        }
        return x;
    }

    public static List<ApproximationResult> computeAll(List<Double> x, List<Double> y) {
        return List.of(
                linear(x, y),
                quadratic(x, y),
                cubic(x, y),
                exponential(x, y),
                logarithmic(x, y),
                power(x, y)
        );
    }
}
