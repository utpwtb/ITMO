package input;

import input.util.InputUtil;
import model.MatrixData;

import java.util.Random;

public class RandomInputHandler {
    private final InputUtil inputUtil;
    private static final int MAX_DIMENSION = 20;
    private final Random random;

    public RandomInputHandler(InputUtil inputUtil) {
        this.inputUtil = inputUtil;
        this.random = new Random();
    }

    public MatrixData readMatrix() {
        Integer n = readDimension();
        
        Double[][] coefficients = generateRandomCoefficients(n);
        Double[] constants = generateRandomConstants(n);
        
        System.out.println("\nСлучайная матрица успешно сгенерирована. Размерность: " + n);
        
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

    private Double[][] generateRandomCoefficients(Integer n) {
        Double[][] coefficients = new Double[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                coefficients[i][j] = generateRandomDouble();
            }
        }

        return coefficients;
    }

    private Double[] generateRandomConstants(Integer n) {
        Double[] constants = new Double[n];

        for (int i = 0; i < n; i++) {
            constants[i] = generateRandomDouble();
        }

        return constants;
    }

    private Double generateRandomDouble() {
        double rangeMin = -100.0;
        double rangeMax = 100.0;
        return rangeMin + (rangeMax - rangeMin) * random.nextDouble();
    }
}
