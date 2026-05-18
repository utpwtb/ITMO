package com.itmo.core.solvers.integration;

import com.itmo.core.functions.Function;

public class MidpointRectangleSolver implements NumericalIntegrationSolver {
    @Override
    public double integrate(Function function, double a, double b, int n) {
        double h = (b - a) / n;
        double sum = 0.0;
        for (int i = 0; i < n; i++) {
            sum += function.evaluate(a + (i + 0.5) * h);
        }
        return h * sum;
    }

    @Override
    public String getMethodName() {
        return "中矩形法";
    }
}
