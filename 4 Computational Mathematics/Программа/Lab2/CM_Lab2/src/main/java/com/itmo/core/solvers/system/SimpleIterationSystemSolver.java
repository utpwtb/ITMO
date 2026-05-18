package com.itmo.core.solvers.system;

import com.itmo.core.model.SystemSolveResult;
import com.itmo.core.functions.SystemInfo;
import com.itmo.core.solvers.system.utils.ConvergenceCheckResult;

import java.util.ArrayList;
import java.util.List;

public class SimpleIterationSystemSolver implements SystemSolver {
    private static final int MAX_ITERATIONS = 1000;

    public ConvergenceCheckResult checkConvergence(SystemInfo system, double x, double y) {
        double dphi1dxVal = system.getDphi1dx().evaluate(x, y);
        double dphi1dyVal = system.getDphi1dy().evaluate(x, y);
        double dphi2dxVal = system.getDphi2dx().evaluate(x, y);
        double dphi2dyVal = system.getDphi2dy().evaluate(x, y);
        return new ConvergenceCheckResult(dphi1dxVal, dphi1dyVal, dphi2dxVal, dphi2dyVal);
    }

    @Override
    public SystemSolveResult solve(SystemInfo system, double x1Init, double x2Init, double epsilon) {
        ConvergenceCheckResult convCheck = checkConvergence(system, x1Init, x2Init);
        if (!convCheck.conditionMet) {
            return new SystemSolveResult(x1Init, x2Init,
                system.getF1().evaluate(x1Init, x2Init),
                system.getF2().evaluate(x1Init, x2Init),
                0, false,
                String.format("Условие сходимости не выполняется: max|φ'(x)| = %.6f ≥ 1", convCheck.jacobianNorm),
                new double[0]);
        }

        double x1 = x1Init;
        double x2 = x2Init;
        int iterations = 0;
        List<Double> errors = new ArrayList<>();

        while (iterations < MAX_ITERATIONS) {
            double newX1 = system.getPhi1().evaluate(x1, x2);
            double newX2 = system.getPhi2().evaluate(x1, x2);

            double error = Math.max(Math.abs(newX1 - x1), Math.abs(newX2 - x2));
            errors.add(error);
            iterations++;

            if (Double.isNaN(newX1) || Double.isInfinite(newX1) ||
                Double.isNaN(newX2) || Double.isInfinite(newX2)) {
                return new SystemSolveResult(x1, x2,
                    system.getF1().evaluate(x1, x2),
                    system.getF2().evaluate(x1, x2),
                    iterations, false, "Итерационный процесс вышел за пределы допустимых значений.",
                    toPrimitiveArray(errors));
            }

            if (error <= epsilon) {
                return new SystemSolveResult(newX1, newX2,
                    system.getF1().evaluate(newX1, newX2),
                    system.getF2().evaluate(newX1, newX2),
                    iterations, true, "Метод сходится.",
                    toPrimitiveArray(errors));
            }

            x1 = newX1;
            x2 = newX2;
        }

        return new SystemSolveResult(x1, x2,
            system.getF1().evaluate(x1, x2),
            system.getF2().evaluate(x1, x2),
            iterations, false, "Превышено максимальное число итераций (" + MAX_ITERATIONS + ").",
            toPrimitiveArray(errors));
    }

    private double[] toPrimitiveArray(List<Double> list) {
        double[] array = new double[list.size()];
        for (int i = 0; i < list.size(); i++) {
            array[i] = list.get(i);
        }
        return array;
    }

    @Override
    public String getMethodName() {
        return "Метод простой итерации";
    }
}
