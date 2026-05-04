package com.itmo.core.solvers.integration;

import com.itmo.core.functions.Function;

public class TrapezoidalSolver implements NumericalIntegrationSolver {
    @Override
    public double integrate(Function function, double a, double b, int n) {
        double h = (b - a) / n;
        double sum = (function.evaluate(a) + function.evaluate(b)) / 2.0;
        for (int i = 1; i < n; i++) {
            sum += function.evaluate(a + i * h);
        }
        return h * sum;
    }

    @Override
    public String getMethodName() {
        return "梯形法";
    }
}
