package com.itmo.core.utils;

import com.itmo.core.functions.Function;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;
import com.itmo.core.utils.models.RungeResult;

public class RungeRule {
    private final NumericalIntegrationSolver solver;

    private final int order;

    public RungeRule(NumericalIntegrationSolver solver) {
        this.solver = solver;
        String methodName = solver.getMethodName();
        if (methodName.contains("левых") || methodName.contains("правых")) {
            this.order = 1;
        } else if (methodName.contains("средних") || methodName.contains("трапеций")) {
            this.order = 2;
        } else {
            this.order = 4;
        }
    }

    public RungeResult compute(Function function, double a, double b, int initialN, double epsilon) {
        int n = initialN;
        double prevResult = 0.0;
        double currentResult;
        double error = Double.MAX_VALUE;
        int iterations = 0;
        final int maxIterations = 10000;

        while (error > epsilon && iterations < maxIterations) {
            currentResult = solver.integrate(function, a, b, n);
            if (iterations > 0) {
                error = Math.abs(currentResult - prevResult) / (Math.pow(2, order) - 1);
                if (error <= epsilon) {
                    return new RungeResult(currentResult, n, error, true, iterations);
                }
            }
            prevResult = currentResult;
            n *= 2;
            iterations++;
        }

        currentResult = solver.integrate(function, a, b, n);
        error = iterations > 0 ? Math.abs(currentResult - prevResult) / (Math.pow(2, order) - 1) : 0;
        return new RungeResult(currentResult, n, error, error <= epsilon, iterations);
    }
}
