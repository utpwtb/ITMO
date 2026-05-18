package input;

import input.util.InputUtil;
import model.MatrixData;

public class KeyInputHandler {
    private final InputUtil inputUtil;
    private static final int MAX_DIMENSION = 20;

    public KeyInputHandler(InputUtil inputUtil) {
        this.inputUtil = inputUtil;
    }

    public MatrixData readMatrix() {
        Integer n = readDimension();
        Double[][] coefficients = readCoefficients(n);
        Double[] constants = readConstants(n);

        return new MatrixData(n, coefficients, constants);
    }

    private Integer readDimension() {
        Integer n;

        while (true) {
            n =
                    inputUtil.getInput(
                            "\nПожалуйста, введите размерность матрицы n (n ≤ " + MAX_DIMENSION + "):",
                            Integer::parseInt,
                            "\nНеверный тип данных, пожалуйста, введите их заново.");

            if (n <= 0) {
                System.out.println("\nРазмерность матрицы должна быть положительным числом.");
                continue;
            }

            if (n > MAX_DIMENSION) {
                System.out.println("\nКоличество размеров не может превышать " + MAX_DIMENSION + ". Пожалуйста, введите данные повторно.");
                continue;
            }
            break;
        }

        return n;
    }

    private Double[][] readCoefficients(Integer n) {
        System.out.println("\nПожалуйста, введите матрицу коэффициентов A (" + n + " строк, " + n + " столбцов):");

        Double[][] coefficientsA = new Double[n][n];

        for (int i = 0; i < coefficientsA.length; i++) {
            for (int j = 0; j < coefficientsA.length; j++) {
                Double input =
                        inputUtil.getInput(
                                "\nПожалуйста, введите элементы матрицы a" + (i + 1) + (j + 1) + " :",
                                Double::parseDouble,
                                "\nНеверный тип данных, пожалуйста, введите их заново.");
                coefficientsA[i][j] = input;
            }

        }

        return coefficientsA;
    }

    private Double[] readConstants(Integer n) {
        System.out.println("\nПожалуйста, введите вектор параметров B.");

        Double[] constants = new Double[n];

        for (int i = 0; i < constants.length; i++) {
            Double input =
                    inputUtil.getInput(
                            "\nПожалуйста, введите элементы матрицы b" + (i + 1) + " :",
                            Double::parseDouble,
                            "\nНеверный тип данных, пожалуйста, введите их заново."
                    );
            constants[i] = input;
        }

        return constants;
    }
}
