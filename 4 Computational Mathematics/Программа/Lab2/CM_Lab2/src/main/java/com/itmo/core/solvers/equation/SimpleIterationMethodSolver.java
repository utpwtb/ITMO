package com.itmo.core.solvers.equation;

import com.itmo.core.model.SolveResult;
import com.itmo.core.model.IterationMethodInfo;
import com.itmo.core.functions.Function;
import com.itmo.core.solvers.equation.utils.InitialApproxSelector;

import java.util.function.DoubleUnaryOperator;

public class SimpleIterationMethodSolver implements EquationSolver {
    private static final int MAX_ITERATIONS = 1000;
    private static final int CHECK_POINTS = 20;

    @Override
    public SolveResult solve(Function f, Function derivative, Function secondDerivative, double a, double b, double epsilon) {
        IterationMethodInfo methodInfo = buildIterationFunction(f, derivative, a, b);

        if (!methodInfo.isCanApply()) {
            return new SolveResult(Double.NaN, Double.NaN, 0, false, methodInfo.getMessage());
        }

        InitialApproxSelector.Result init = InitialApproxSelector.selectByNewtonRule(f, secondDerivative, a, b);
        if (!init.valid) {
            return new SolveResult(Double.NaN, Double.NaN, 0, false, init.message);
        }

        DoubleUnaryOperator phi = methodInfo.getPhi();
        DoubleUnaryOperator phiDerivative = methodInfo.getPhiDerivative();

        double q = computeMaxPhiPrime(phiDerivative, a, b);
        double x0 = init.x0;
        int iterations = 0;

        while (iterations < MAX_ITERATIONS) {
            double x1 = phi.applyAsDouble(x0);
            iterations++;

            if (Double.isNaN(x1) || Double.isInfinite(x1)) {
                return new SolveResult(x0, f.evaluate(x0), iterations, false,
                    "Итерационный процесс вышел за пределы допустимых значений.");
            }

            double threshold = q <= 0.5 ? epsilon : (1 - q) / q * epsilon;

            if (Math.abs(x1 - x0) < threshold) {
                double fValue = f.evaluate(x1);
                if (Math.abs(fValue) < epsilon) {
                    return new SolveResult(x1, fValue, iterations, true,
                        methodInfo.getMessage() + " Метод сходится.");
                }
            }

            x0 = x1;
        }

        return new SolveResult(x0, f.evaluate(x0), iterations, false,
            "Превышено максимальное число итераций (" + MAX_ITERATIONS + ").");
    }

    private IterationMethodInfo buildIterationFunction(Function f, Function df, double a, double b) {
        double h = (b - a) / CHECK_POINTS;
        double maxAbsDerivative = 0;
        boolean fPrimePositive = true;
        boolean fPrimeNegative = true;

        for (int i = 0; i <= CHECK_POINTS; i++) {
            double x = a + i * h;
            double dfVal = df.evaluate(x);
            maxAbsDerivative = Math.max(maxAbsDerivative, Math.abs(dfVal));
            if (dfVal > 0) fPrimeNegative = false;
            if (dfVal < 0) fPrimePositive = false;
        }

        if (maxAbsDerivative < 1e-10) {
            return new IterationMethodInfo(null, null,
                "Производная близка к нулю. Невозможно построить итерационную функцию.", false);
        }

        if (!fPrimePositive && !fPrimeNegative) {
            return new IterationMethodInfo(null, null,
                String.format("f'(x) меняет знак на интервале [%.4f, %.4f]. " +
                    "Невозможно гарантировать сходимость метода простой итерации.", a, b), false);
        }

        double lambda = fPrimePositive ? -1.0 / maxAbsDerivative : 1.0 / maxAbsDerivative;

        DoubleUnaryOperator phi = x -> x + lambda * f.evaluate(x);
        DoubleUnaryOperator phiDerivative = x -> 1 + lambda * df.evaluate(x);

        boolean conditionMet = checkConvergenceCondition(phiDerivative, a, b);

        String message;
        if (conditionMet) {
            message = String.format("Условие сходимости |φ'(x)| < 1 выполняется на интервале. λ = %.6f", lambda);
        } else {
            message = String.format("Предупреждение: условие сходимости |φ'(x)| < 1 может не выполняться на всем интервале. λ = %.6f", lambda);
        }

        return new IterationMethodInfo(phi, phiDerivative, message, true);
    }

    private boolean checkConvergenceCondition(DoubleUnaryOperator phiDerivative, double a, double b) {
        double h = (b - a) / CHECK_POINTS;

        for (int i = 0; i <= CHECK_POINTS; i++) {
            double x = a + i * h;
            if (Math.abs(phiDerivative.applyAsDouble(x)) >= 1) {
                return false;
            }
        }
        return true;
    }

    private double computeMaxPhiPrime(DoubleUnaryOperator phiDerivative, double a, double b) {
        double h = (b - a) / CHECK_POINTS;
        double maxVal = 0;

        for (int i = 0; i <= CHECK_POINTS; i++) {
            double x = a + i * h;
            maxVal = Math.max(maxVal, Math.abs(phiDerivative.applyAsDouble(x)));
        }
        return maxVal;
    }

    @Override
    public String getMethodName() {
        return "Метод простой итерации";
    }
}
