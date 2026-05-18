package com.itmo.core.solvers.integration;

import com.itmo.core.functions.Function;

public class SimpsonSolver implements NumericalIntegrationSolver {
    @Override
    public double integrate(Function function, double a, double b, int n) {
        if (n % 2 != 0) n++;
        double h = (b - a) / n;
        double sum = function.evaluate(a) + function.evaluate(b);
        for (int i = 1; i < n; i++) {
            double x = a + i * h;
            if (i % 2 == 0) {
                sum += 2 * function.evaluate(x);
            } else {
                sum += 4 * function.evaluate(x);
            }
        }
        return h / 3.0 * sum;
    }

    @Override
    public String getMethodName() {
        return "辛普森法";
    }
}
