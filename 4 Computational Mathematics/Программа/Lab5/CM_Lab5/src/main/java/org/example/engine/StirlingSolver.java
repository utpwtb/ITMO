package org.example.engine;

import org.example.model.InterpolationResult;

public class StirlingSolver {

    /** Stirling formula = (Gauss forward + Gauss backward) / 2 */
    public static InterpolationResult interpolate(double[] x, double[] y,
                                                  double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;
        double q = (xTarget - x[c]) / h;

        double gf = gaussForwardEval(ft, c, q, n);
        double gb = gaussBackwardEval(ft, c, q, n);
        double result = (gf + gb) / 2.0;

        return new InterpolationResult(
                "Stirling Formula", xTarget, result, ft, n - 1);
    }

    private static double gaussForwardEval(double[][] ft, int c, double q, int n) {
        double result = ft[c][0];
        for (int k = 1; k < n; k++) {
            double coeff = gaussForwardCoeff(q, k);
            int row;
            if (k % 2 == 1) {
                row = c - (k - 1) / 2;
            } else {
                row = c - k / 2;
            }
            if (row >= 0 && row < n - k) {
                result += coeff * ft[row][k];
            }
        }
        return result;
    }

    private static double gaussBackwardEval(double[][] ft, int c, double q, int n) {
        double result = ft[c][0];
        for (int k = 1; k < n; k++) {
            double coeff = gaussBackwardCoeff(q, k);
            int row;
            if (k % 2 == 1) {
                row = c - (k + 1) / 2;
            } else {
                row = c - k / 2;
            }
            if (row >= 0 && row < n - k) {
                result += coeff * ft[row][k];
            }
        }
        return result;
    }

    private static double gaussForwardCoeff(double q, int k) {
        double prod = 1.0;
        if (k % 2 == 1) {
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (q + s);
            }
        } else {
            int start = -k / 2;
            int end = k / 2 - 1;
            for (int s = start; s <= end; s++) {
                prod *= (q + s);
            }
        }
        return prod / factorial(k);
    }

    private static double gaussBackwardCoeff(double q, int k) {
        double prod = 1.0;
        if (k % 2 == 1) {
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (q + s);
            }
        } else {
            int start = -(k / 2 - 1);
            int end = k / 2;
            for (int s = start; s <= end; s++) {
                prod *= (q + s);
            }
        }
        return prod / factorial(k);
    }

    private static double factorial(int k) {
        double f = 1.0;
        for (int i = 2; i <= k; i++) f *= i;
        return f;
    }
}
