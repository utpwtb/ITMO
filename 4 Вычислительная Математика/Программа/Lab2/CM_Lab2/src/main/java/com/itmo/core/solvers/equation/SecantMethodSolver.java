package com.itmo.core.solvers.equation;

import com.itmo.core.model.SolveResult;
import com.itmo.core.model.RootCheckResult;
import com.itmo.core.functions.Function;
import com.itmo.core.solvers.equation.utils.InitialApproxSelector;
import com.itmo.core.solvers.equation.utils.IntervalRootChecker;

public class SecantMethodSolver implements EquationSolver {
    private static final int MAX_ITERATIONS = 1000;

    @Override
    public SolveResult solve(Function f, Function derivative, Function secondDerivative, double a, double b, double epsilon) {
        RootCheckResult rootCheck = new IntervalRootChecker().checkRoot(f, a, b, 100);
        if (!rootCheck.hasRoot()) {
            return new SolveResult(Double.NaN, Double.NaN, 0, false,
                "На интервале [" + a + ", " + b + "] корней не обнаружено. " + rootCheck.getMessage());
        }
        if (rootCheck.getRootCount() > 1) {
            return new SolveResult(Double.NaN, Double.NaN, 0, false,
                "На интервале обнаружено несколько корней (" + rootCheck.getRootCount() + "). " +
                "Рекомендуется сузить интервал для изоляции одного корня.");
        }

        InitialApproxSelector.Result init = InitialApproxSelector.selectByNewtonRule(f, secondDerivative, a, b);
        if (!init.valid) {
            return new SolveResult(Double.NaN, Double.NaN, 0, false, init.message);
        }

        double x0 = init.x0;
        double x1 = x0 + epsilon;

        double f0 = f.evaluate(x0);
        double f1 = f.evaluate(x1);

        int iterations = 0;

        while (iterations < MAX_ITERATIONS) {
            if (Math.abs(f1 - f0) < 1e-15) {
                return new SolveResult(x1, f1, iterations, false,
                    "Деление на ноль: f(x_i) ≈ f(x_{i-1}). Метод не сходится.");
            }

            double x2 = x1 - (x1 - x0) / (f1 - f0) * f1;
            double f2 = f.evaluate(x2);
            iterations++;

            if (Math.abs(f2) < epsilon) {
                return new SolveResult(x2, f2, iterations, true, "Метод секущих сходится.");
            }

            x0 = x1;
            f0 = f1;
            x1 = x2;
            f1 = f2;
        }

        return new SolveResult(x1, f1, iterations, false,
            "Превышено максимальное число итераций (" + MAX_ITERATIONS + ").");
    }

    @Override
    public String getMethodName() {
        return "Метод секущих";
    }
}
