package org.example.engine;

import org.example.engine.util.CentralDifferenceUtils;
import org.example.model.InterpolationResult;

public class GaussSolver {

    /** Gauss 1st formula (forward) - for points after the central node */
    public static InterpolationResult interpolateForward(double[] x, double[] y,
                                                         double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;
        double t = (xTarget - x[c]) / h;
        double result = ft[c][0];

        for (int k = 1; k < n; k++) {
            double coeff = CentralDifferenceUtils.gaussForwardCoeff(t, k);
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
                "Гаусс 1-я формула (вперёд)", xTarget, result, ft, n - 1);
    }

    /** Gauss 2nd formula (backward) - for points before the central node */
    public static InterpolationResult interpolateBackward(double[] x, double[] y,
                                                          double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;
        double t = (xTarget - x[c]) / h;
        double result = ft[c][0];

        for (int k = 1; k < n; k++) {
            double coeff = CentralDifferenceUtils.gaussBackwardCoeff(t, k);
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
                "Гаусс 2-я формула (назад)", xTarget, result, ft, n - 1);
    }
}
