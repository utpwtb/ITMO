package com.itmo.core.utils;

import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;
import com.itmo.core.utils.ImproperIntegralHandler.IntegrationWithDiscontinuity;
import com.itmo.core.utils.RungeRule.RungeResult;

public class ResultFormatter {

    public static void printHeader() {
        System.out.println("========================================");
        System.out.println("   数值积分计算程序 (Lab3)");
        System.out.println("========================================\n");
    }

    public static void printFunctionList(java.util.List<IntegralFunctionInfo> functions) {
        System.out.println("可用函数列表:");
        for (int i = 0; i < functions.size(); i++) {
            IntegralFunctionInfo f = functions.get(i);
            String type = f.isImproper() ? " [广义]" : "";
            System.out.printf("  %d. %s%s\n", i + 1, f.getName(), type);
        }
        System.out.println();
    }

    public static void printSolverList(java.util.List<NumericalIntegrationSolver> solvers) {
        System.out.println("可选积分方法:");
        for (int i = 0; i < solvers.size(); i++) {
            System.out.printf("  %d. %s\n", i + 1, solvers.get(i).getMethodName());
        }
        System.out.printf("  %d. 全部方法\n", solvers.size() + 1);
        System.out.println();
    }

    public static void printComputationSummary(IntegralFunctionInfo func,
                                               double a, double b, double epsilon, int initialN) {
        System.out.println("\n----------------------------------------");
        System.out.printf("函数: %s\n", func.getName());
        System.out.printf("区间: [%.6f, %.6f]\n", a, b);
        System.out.printf("精度: %.10f\n", epsilon);
        System.out.printf("初始分割数: n=%d\n", initialN);
        System.out.println("----------------------------------------\n");
    }

    public static void printRegularResult(NumericalIntegrationSolver solver, RungeResult result) {
        System.out.printf("【%s】\n", solver.getMethodName());
        System.out.printf("  积分值: %.10f\n", result.getValue());
        System.out.printf("  分割数: n = %d\n", result.getN());
        System.out.printf("  估计误差: %.2e\n", result.getError());
        System.out.printf("  迭代次数: %d\n", result.getIterations());
        if (!result.isConverged()) {
            System.out.println("  ⚠ 未在最大迭代次数内达到要求精度");
        }
        System.out.println();
    }

    public static void printDivergentResult(String message) {
        System.out.println("积分不存在");
    }

    public static void printConvergentResult(String message) {
    }

    public static void printImproperResult(NumericalIntegrationSolver solver,
                                           IntegrationWithDiscontinuity result) {
        System.out.printf("【%s - 广义积分计算】\n", solver.getMethodName());
        if (result.success()) {
            System.out.printf("  积分值: %.10f\n", result.value());
            System.out.printf("  最大分割数: n = %d\n", result.maxN());
            System.out.println("  计算详情:");
            for (String line : result.detailLog().split("\n")) {
                System.out.println("    " + line);
            }
        } else {
            System.out.println("  ❌ 计算失败: " + result.errorMessage());
        }
        System.out.println();
    }
}
