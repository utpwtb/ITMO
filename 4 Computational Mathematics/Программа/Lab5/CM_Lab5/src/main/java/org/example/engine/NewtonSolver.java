package org.example.engine;

import org.example.model.InterpolationResult;

public class NewtonSolver {

    private static double[][] buildDividedDiffTable(double[] x, double[] y) {
        int n = y.length;
        double[][] table = new double[n][n];
        for (int i = 0; i < n; i++) {
            table[i][0] = y[i];
        }
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < n - j; i++) {
                table[i][j] = (table[i + 1][j - 1] - table[i][j - 1])
                        / (x[i + j] - x[i]);
            }
        }
        return table;
    }

    public static InterpolationResult interpolateForward(double[] x, double[] y,
                                                         double xTarget) {
        double[][] dd = buildDividedDiffTable(x, y);
        int n = x.length;
        double result = dd[0][0];
        double product = 1.0;

        for (int i = 1; i < n; i++) {
            product *= (xTarget - x[i - 1]);
            result += dd[0][i] * product;
        }

        double[][] fd = FiniteDifferenceTable.build(y);
        return new InterpolationResult(
                "Ньютон (вперёд)", xTarget, result, fd, n - 1
        );
    }

    public static InterpolationResult interpolateBackward(double[] x, double[] y,
                                                          double xTarget) {
        double[][] dd = buildDividedDiffTable(x, y);
        int n = x.length;
        double result = dd[n - 1][0];
        double product = 1.0;

        for (int i = 1; i < n; i++) {
            product *= (xTarget - x[n - i]);
            result += dd[n - 1 - i][i] * product;
        }

        double[][] fd = FiniteDifferenceTable.build(y);
        return new InterpolationResult(
                "Ньютон (назад)", xTarget, result, fd, n - 1
        );
    }

}
