package com.itmo.core.utils;

import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;
import com.itmo.core.utils.models.IntegrationWithDiscontinuity;
import com.itmo.core.utils.models.RungeResult;

public class ResultFormatter {

    public static void printFunctionList(java.util.List<IntegralFunctionInfo> functions) {
        System.out.println("Доступные функции:");
        for (int i = 0; i < functions.size(); i++) {
            System.out.printf("  %d. %s\n", i + 1, functions.get(i).getName());
        }
        System.out.println();
    }

    public static void printSolverList(java.util.List<NumericalIntegrationSolver> solvers) {
        System.out.println("Методы интегрирования:");
        for (int i = 0; i < solvers.size(); i++) {
            System.out.printf("  %d. %s\n", i + 1, solvers.get(i).getMethodName());
        }
        System.out.println();
    }

    public static void printComputationSummary(IntegralFunctionInfo func,
                                               double a, double b, double epsilon, int initialN) {
        System.out.printf("Функция: %s\n", func.getName());
        System.out.printf("Отрезок: [%.6f, %.6f]\n", a, b);
        System.out.printf("Точность: %.10f\n", epsilon);
        System.out.println();
    }

    public static void printRegularResult(NumericalIntegrationSolver solver, RungeResult result) {
        System.out.printf("【%s】\n", solver.getMethodName());
        System.out.printf("  Значение: %.10f\n", result.getValue());
        System.out.printf("  Разбиений: n = %d\n", result.getN());
        System.out.printf("  Ошибка: %.2e\n", result.getError());
        if (!result.isConverged()) {
            System.out.println("Требуемая точность не достигнута");
        }
        System.out.println();
    }

    public static void printDivergentResult(String message) {
        System.out.println("Интеграл не существует");
    }

    public static void printImproperResult(NumericalIntegrationSolver solver,
                                           IntegrationWithDiscontinuity result) {
        System.out.printf("【%s】\n", solver.getMethodName());
        if (result.success()) {
            System.out.printf("  Значение: %.10f\n", result.value());
            System.out.printf("  Макс. разбиений: n = %d\n", result.maxN());
            for (String line : result.detailLog().split("\n")) {
                System.out.println("    " + line);
            }
        } else {
            System.out.println("Ошибка вычисления: " + result.errorMessage());
        }
        System.out.println();
    }
}
