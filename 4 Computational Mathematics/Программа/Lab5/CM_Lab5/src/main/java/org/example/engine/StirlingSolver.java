package org.example.engine;

import org.example.engine.util.CentralDifferenceUtils;
import org.example.model.InterpolationResult;

public class StirlingSolver {

    /** Stirling formula = (Gauss forward + Gauss backward) / 2 */
    public static InterpolationResult interpolate(double[] x, double[] y,
                                                  double xTarget) {
        int n = y.length;
        double[][] ft = FiniteDifferenceTable.build(y);
        double h = x[1] - x[0];
        int c = n / 2;
        double t = (xTarget - x[c]) / h;

        double gf = gaussForwardEval(ft, c, t, n);
        double gb = gaussBackwardEval(ft, c, t, n);
        double result = (gf + gb) / 2.0;

        return new InterpolationResult(
                "Формула Стирлинга", xTarget, result, ft, n - 1);
    }

    private static double gaussForwardEval(double[][] ft, int c, double t, int n) {
        double result = ft[c][0];
        for (int k = 1; k < n; k++) {
            double coeff = CentralDifferenceUtils.gaussForwardCoeff(t, k);
            int row = (k % 2 == 1) ? c - (k - 1) / 2 : c - k / 2;
            if (row >= 0 && row < n - k) {
                result += coeff * ft[row][k];
            }
        }
        return result;
    }

    private static double gaussBackwardEval(double[][] ft, int c, double t, int n) {
        double result = ft[c][0];
        for (int k = 1; k < n; k++) {
            double coeff = CentralDifferenceUtils.gaussBackwardCoeff(t, k);
            int row = (k % 2 == 1) ? c - (k + 1) / 2 : c - k / 2;
            if (row >= 0 && row < n - k) {
                result += coeff * ft[row][k];
            }
        }
        return result;
    }
}
