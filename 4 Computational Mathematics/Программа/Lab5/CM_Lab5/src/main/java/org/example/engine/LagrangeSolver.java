package org.example.engine;

import org.example.model.InterpolationResult;

public class LagrangeSolver {

    public static InterpolationResult interpolate(double[] x, double[] y, double xTarget) {
        int n = x.length;
        double result = 0.0;

        for (int i = 0; i < n; i++) {
            double term = y[i];
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    term *= (xTarget - x[j]) / (x[i] - x[j]);
                }
            }
            result += term;
        }

        double[][] diffTable = FiniteDifferenceTable.build(y);
        return new InterpolationResult(
                "Полином Лагранжа", xTarget, result, diffTable, n - 1
        );
    }
}
