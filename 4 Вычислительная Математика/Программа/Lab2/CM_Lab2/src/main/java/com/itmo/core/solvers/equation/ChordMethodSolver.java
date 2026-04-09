package com.itmo.core.solvers.equation;

import com.itmo.core.model.SolveResult;
import com.itmo.core.model.RootCheckResult;
import com.itmo.core.functions.Function;
import com.itmo.core.solvers.equation.utils.IntervalRootChecker;

public class ChordMethodSolver implements EquationSolver {
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

        double fa = f.evaluate(a);
        double fb = f.evaluate(b);

        int iterations = 0;
        double ai = a, bi = b;
        double fai = fa, fbi = fb;

        while (iterations < MAX_ITERATIONS) {
            if (Math.abs(fbi - fai) < 1e-15) {
                return new SolveResult(ai, fai, iterations, false,
                        "Деление на ноль: f(b_i) ≈ f(a_i). Метод не сходится.");
            }

            double xi = ai - ((bi - ai) * fai) / (fbi - fai);
            double fi = f.evaluate(xi);
            iterations++;

            if (Math.abs(fi) < epsilon) {
                return new SolveResult(xi, fi, iterations, true, "Метод хорд сходится.");
            }

            if (fai * fi < 0) {
                bi = xi;
                fbi = fi;
            } else {
                ai = xi;
                fai = fi;
            }
        }

        return new SolveResult((ai + bi) / 2, f.evaluate((ai + bi) / 2), iterations, false,
                "Превышено максимальное число итераций (" + MAX_ITERATIONS + ").");
    }

    @Override
    public String getMethodName() {
        return "Метод хорд";
    }
}
