package org.example.engine;

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
            if (Math.abs(coeff) < 1e-15) continue;

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
                "Bessel Formula", xTarget, result, ft, n - 1);
    }

    /** Bessel coefficients: product of (q - shift_i) / k! */
    private static double besselCoeff(double q, int k) {
        switch (k) {
            case 1:  return q;
            case 2:  return q * (q - 1) / 2.0;
            case 3:  return q * (q - 1) * (q - 0.5) / 6.0;
            case 4:  return (q + 1) * q * (q - 1) * (q - 2) / 24.0;
            case 5:  return (q + 1) * q * (q - 1) * (q - 2) * (q - 0.5) / 120.0;
            case 6:  return (q + 2) * (q + 1) * q * (q - 1) * (q - 2) * (q - 3) / 720.0;
            default: return 0;
        }
    }
}
