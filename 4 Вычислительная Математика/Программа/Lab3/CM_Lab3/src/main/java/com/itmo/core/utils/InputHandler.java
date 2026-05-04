package com.itmo.core.utils;

import com.itmo.core.functions.IntegralFunctionInfo;
import com.itmo.core.solvers.integration.NumericalIntegrationSolver;

import java.util.List;
import java.util.Scanner;

public class InputHandler {
    private final Scanner scanner;

    public InputHandler(Scanner scanner) {
        this.scanner = scanner;
    }

    public IntegralFunctionInfo selectFunction(List<IntegralFunctionInfo> functions) {
        while (true) {
            System.out.print("请选择函数编号 (1-" + functions.size() + "): ");
            try {
                int choice = Integer.parseInt(scanner.nextLine().trim());
                if (choice >= 1 && choice <= functions.size()) {
                    return functions.get(choice - 1);
                }
                System.out.println("无效编号，请重新输入。");
            } catch (NumberFormatException e) {
                System.out.println("请输入有效数字。");
            }
        }
    }

    public List<NumericalIntegrationSolver> selectSolvers(List<NumericalIntegrationSolver> solvers) {
        int maxChoice = solvers.size() + 1;
        while (true) {
            System.out.printf("请选择积分方法编号 (1-%d): ", maxChoice);
            try {
                String input = scanner.nextLine().trim();
                if ("all".equalsIgnoreCase(input)) {
                    return solvers;
                }
                int choice = Integer.parseInt(input);
                if (choice >= 1 && choice <= solvers.size()) {
                    return List.of(solvers.get(choice - 1));
                } else if (choice == maxChoice) {
                    return solvers;
                }
                System.out.println("无效编号，请重新输入。");
            } catch (NumberFormatException e) {
                System.out.println("请输入有效数字。");
            }
        }
    }

    public double readDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                return Double.parseDouble(scanner.nextLine().trim());
            } catch (NumberFormatException e) {
                System.out.println("无效输入，请输入一个数字。");
            }
        }
    }

    public boolean wantContinue() {
        while (true) {
            System.out.print("\n是否继续计算？(y/n): ");
            String input = scanner.nextLine().trim().toLowerCase();
            if ("y".equals(input) || "yes".equals(input) || "是".equals(input)) {
                return true;
            }
            if ("n".equals(input) || "no".equals(input) || "否".equals(input) || "".equals(input)) {
                return false;
            }
            System.out.println("请输入 y/n");
        }
    }
}
