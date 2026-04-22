package com.itmo.core.solvers.integration;

import com.itmo.core.functions.Function;

public class RightRectangleSolver implements NumericalIntegrationSolver {
    @Override
    public double integrate(Function function, double a, double b, int n) {
        double h = (b - a) / n;
        double sum = 0.0;
        for (int i = 1; i <= n; i++) {
            sum += function.evaluate(a + i * h);
        }
        return h * sum;
    }

    @Override
    public String getMethodName() {
        return "Метод правых прямоугольников";
    }
}
