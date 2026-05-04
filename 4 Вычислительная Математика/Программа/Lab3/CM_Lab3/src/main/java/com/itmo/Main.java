package com.itmo;

import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.functions.IntegralRepository;
import com.itmo.core.solvers.integration.*;
import com.itmo.core.utils.InputHandler;
import com.itmo.core.utils.IntegrationEngine;
import com.itmo.core.utils.ResultFormatter;

import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        InputHandler input = new InputHandler(scanner);
        List<NumericalIntegrationSolver> allSolvers = List.of(
                new LeftRectangleSolver(),
                new RightRectangleSolver(),
                new MidpointRectangleSolver(),
                new TrapezoidalSolver(),
                new SimpsonSolver()
        );

        do {
            ResultFormatter.printHeader();

            List<IntegralFunctionInfo> allFunctions = IntegralRepository.getAllFunctions();
            ResultFormatter.printFunctionList(allFunctions);

            IntegralFunctionInfo selectedFunc = input.selectFunction(allFunctions);
            double a = input.readDouble("请输入积分下限 a: ");
            double b = input.readDouble("请输入积分上限 b: ");
            double epsilon = input.readDouble("请输入计算精度 ε: ");

            ResultFormatter.printSolverList(allSolvers);
            List<NumericalIntegrationSolver> selectedSolvers = input.selectSolvers(allSolvers);

            ResultFormatter.printComputationSummary(selectedFunc, a, b, epsilon, IntegrationEngine.getInitialN());

            if (selectedFunc.isImproper()) {
                IntegrationEngine.computeImproper(selectedFunc, selectedSolvers, a, b, epsilon);
            } else {
                IntegrationEngine.computeRegular(selectedFunc, selectedSolvers, a, b, epsilon);
            }
        } while (input.wantContinue());

        System.out.println("\n感谢使用，再见！");
        scanner.close();
    }
}
