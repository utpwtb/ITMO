package org.example.engine;

import org.example.engine.util.CentralDifferenceUtils;
import org.example.model.InterpolationResult;

public class BesselSolver {

    /** Bessel formula - best when |q| ≈ 0.5, uses center x0 and x1 */
    public static InterpolationResult interpolate(double[] x, double[] y,
                                                  double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;  // central index (x0), x1 = x[c+1]
        double q = (xTarget - x[c]) / h;
        double result = ft[c][0];

        for (int k = 1; k < n; k++) {
            double coeff = besselCoeff(q, k);
            if (Math.abs(coeff) < 1e-15) {
                continue;
            }

            double diffVal;
            if (k % 2 == 0) {
                // Even k: average of two adjacent even differences
                int row1 = c - k / 2;
                int row2 = c - k / 2 + 1;
                if (row1 >= 0 && row1 < n - k && row2 >= 0 && row2 < n - k) {
                    diffVal = (ft[row1][k] + ft[row2][k]) / 2.0;
                } else if (row1 >= 0 && row1 < n - k) {
                    diffVal = ft[row1][k];
                } else if (row2 >= 0 && row2 < n - k) {
                    diffVal = ft[row2][k];
                } else {
                    continue;
                }
            } else {
                // Odd k: single odd difference
                int row = c - (k - 1) / 2;
                if (row >= 0 && row < n - k) {
                    diffVal = ft[row][k];
                } else {
                    continue;
                }
            }
            result += coeff * diffVal;
        }

        return new InterpolationResult(
                "Формула Бесселя", xTarget, result, ft, n - 1);
    }

    /**
     * Bessel coefficients using general term formula.
     *
     * For k = 1: product = t
     * For even k = 2m (m >= 1):
     *   product = (t - m) * Prod_{i=-(m-1)}^{m-1} (t + i) / k!
     * For odd k = 2m+1 (m >= 1):
     *   product = (t - 1/2) * (t - m) * Prod_{i=-(m-1)}^{m-1} (t + i) / k!
     */
    private static double besselCoeff(double t, int k) {
        if (k == 1) {
            return t;
        }

        double prod = 1.0;

        if (k % 2 == 0) {
            // even k = 2m
            int m = k / 2;
            for (int i = -(m - 1); i <= m - 1; i++) {
                prod *= (t + i);
            }
            prod *= (t - m);
        } else {
            // odd k = 2m + 1 (m >= 1)
            int m = (k - 1) / 2;
            prod *= (t - 0.5);
            for (int i = -(m - 1); i <= m - 1; i++) {
                prod *= (t + i);
            }
            prod *= (t - m);
        }

        return prod / CentralDifferenceUtils.factorial(k);
    }

}
