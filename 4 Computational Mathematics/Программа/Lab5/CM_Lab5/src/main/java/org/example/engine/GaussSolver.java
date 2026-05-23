package org.example.engine;

import org.example.model.InterpolationResult;

public class GaussSolver {

    /** Gauss 1st formula (forward) - for points after the central node */
    public static InterpolationResult interpolateForward(double[] x, double[] y,
                                                         double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;  // central index
        double q = (xTarget - x[c]) / h;
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

        return new InterpolationResult(
                "Gauss 1st Formula (Forward)", xTarget, result, ft, n - 1);
    }

    /** Gauss 2nd formula (backward) - for points before the central node */
    public static InterpolationResult interpolateBackward(double[] x, double[] y,
                                                          double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;
        double q = (xTarget - x[c]) / h;
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

        return new InterpolationResult(
                "Gauss 2nd Formula (Backward)", xTarget, result, ft, n - 1);
    }

    /** Auto-select based on q sign */
    public static InterpolationResult interpolate(double[] x, double[] y,
                                                  double xTarget) {
        int c = y.length / 2;
        double q = (xTarget - x[c]) / (x[1] - x[0]);
        if (q >= 0) {
            return interpolateForward(x, y, xTarget);
        } else {
            return interpolateBackward(x, y, xTarget);
        }
    }

    private static double gaussForwardCoeff(double q, int k) {
        double prod = 1.0;
        if (k % 2 == 1) {
            // odd: shifts from -(k-1)/2 to (k-1)/2
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (q + s);
            }
        } else {
            // even: shifts from -k/2 to k/2-1
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
            // odd: shifts from -(k-1)/2 to (k-1)/2
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (q + s);
            }
        } else {
            // even: shifts from -(k/2-1) to k/2
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
