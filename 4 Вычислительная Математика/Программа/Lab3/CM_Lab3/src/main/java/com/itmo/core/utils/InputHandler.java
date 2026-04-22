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
            System.out.print("Выберите функцию (1-" + functions.size() + "): ");
            try {
                int choice = Integer.parseInt(scanner.nextLine().trim());
                if (choice >= 1 && choice <= functions.size()) {
                    return functions.get(choice - 1);
                }
                System.out.println("Неверный номер, попробуйте снова.");
            } catch (NumberFormatException e) {
                System.out.println("Введите число.");
            }
        }
    }

    public List<NumericalIntegrationSolver> selectSolvers(List<NumericalIntegrationSolver> solvers) {
        while (true) {
            System.out.printf("Выберите метод (1-%d): ", solvers.size());
            try {
                int choice = Integer.parseInt(scanner.nextLine().trim());
                if (choice >= 1 && choice <= solvers.size()) {
                    return List.of(solvers.get(choice - 1));
                }
                System.out.println("Неверный номер, попробуйте снова.");
            } catch (NumberFormatException e) {
                System.out.println("Введите число.");
            }
        }
    }

    public double readDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                return Double.parseDouble(scanner.nextLine().trim().replace(',', '.'));
            } catch (NumberFormatException e) {
                System.out.println("Неверный ввод, введите число.");
            }
        }
    }

    public boolean wantContinue() {
        while (true) {
            System.out.print("\nПродолжить? (y/n): ");
            String input = scanner.nextLine().trim().toLowerCase();
            if ("y".equals(input) || "yes".equals(input) || "да".equals(input)) {
                return true;
            }
            if ("n".equals(input) || "no".equals(input) || "нет".equals(input) || "".equals(input)) {
                return false;
            }
            System.out.println("Введите y/n");
        }
    }
}
