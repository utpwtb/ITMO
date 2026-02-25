import input.FileInputHandler;
import input.KeyInputHandler;
import input.RandomInputHandler;
import input.util.InputUtil;
import model.MatrixData;
import model.SolutionResult;
import output.ResultPrinter;
import solver.GaussianEliminationSolver;

import java.util.Scanner;


public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("=== Решение системы линейных уравнений методом Гаусса с выбором главного элемента ===");
            System.out.println("Выберите способ ввода:");
            System.out.println("1. Ввод с клавиатуры");
            System.out.println("2. Чтение из файла");
            System.out.println("3. Генерация случайной матрицы");
            System.out.println("4. Выход");
            System.out.print("Введите выбор (1, 2, 3 или 4): ");

            int choice = scanner.nextInt();

            MatrixData matrixData = null;
            if (choice == 1) {
                KeyInputHandler keyInputHandler =
                        new KeyInputHandler(new InputUtil(new Scanner(System.in)));
                matrixData = keyInputHandler.readMatrix();
                if (matrixData == null) {
                    System.out.println("Ошибка чтения данных матрицы.");
                    continue;
                }
            } else if (choice == 2) {
                FileInputHandler fileInputHandler =
                        new FileInputHandler(new Scanner(System.in));
                matrixData = fileInputHandler.readMatrix();
                if (matrixData == null) {
                    System.out.println("Ошибка чтения данных матрицы.");
                    continue;
                }
            } else if (choice == 3) {
                RandomInputHandler randomInputHandler =
                        new RandomInputHandler(new InputUtil(new Scanner(System.in)));
                matrixData = randomInputHandler.readMatrix();
                if (matrixData == null) {
                    System.out.println("Ошибка генерации случайной матрицы.");
                    continue;
                }
            } else if (choice == 4) {
                System.out.println("Выход из программы.");
                System.exit(0);
            } else {
                System.out.println("Неверный выбор способа ввода. Пожалуйста, повторите ввод.");
                continue;
            }

            GaussianEliminationSolver gaussianEliminationSolver =
                    new GaussianEliminationSolver();

            SolutionResult result = gaussianEliminationSolver.solve(matrixData);

            ResultPrinter printer = new ResultPrinter();
            printer.print(result, matrixData);
        }
    }


}
