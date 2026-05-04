package com.itmo.core.utils;

import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;
import com.itmo.core.utils.ImproperIntegralHandler.IntegrationWithDiscontinuity;

public class IntegrationEngine {
    private static final int INITIAL_N = 4;

    public static void computeRegular(IntegralFunctionInfo func,
                                      java.util.List<NumericalIntegrationSolver> solvers,
                                      double a, double b, double epsilon) {
        for (NumericalIntegrationSolver solver : solvers) {
            RungeRule runge = new RungeRule(solver);
            RungeRule.RungeResult result = runge.compute(func.getFunction(), a, b, INITIAL_N, epsilon);
            ResultFormatter.printRegularResult(solver, result);
        }
    }

    public static void computeImproper(IntegralFunctionInfo func,
                                       java.util.List<NumericalIntegrationSolver> solvers,
                                       double a, double b, double epsilon) {
        ImproperIntegralHandler.ConvergenceCheck convCheck =
                ImproperIntegralHandler.checkConvergence(func, a, b);

        if (!convCheck.converges()) {
            ResultFormatter.printDivergentResult(convCheck.message());
            return;
        }

        for (NumericalIntegrationSolver solver : solvers) {
            IntegrationWithDiscontinuity result =
                    ImproperIntegralHandler.computeWithDiscontinuities(
                            func, solver, a, b, INITIAL_N, epsilon);
            ResultFormatter.printImproperResult(solver, result);
        }
    }

    public static int getInitialN() {
        return INITIAL_N;
    }
}
