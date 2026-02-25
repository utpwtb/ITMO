package output;

import model.MatrixData;
import model.SolutionResult;

public class ResultPrinter {
    public void print(SolutionResult result, MatrixData originalData) {
        if (!result.isSingular()) {
            System.out.println("\nМатрица является сингулярной и не может быть решена.");
            return;
        }

        printMatrixInfo(originalData.getCoefficients(), originalData.getConstants());

        System.out.println("\n================= Результаты расчетов =================");
        printDeterminant(result);
        printUpperTriangularMatrix(result);
        printSolution(result);
        printResidual(result);
        printVerification(result, originalData);
        System.out.println("\n==============================================");
    }

    private void printMatrixInfo(Double[][] coefficients, Double[] constants) {
        System.out.println("Исходная матрица:");
        for (int i = 0; i < coefficients.length; i++) {
            System.out.print("| ");
            for (int j = 0; j < coefficients[i].length; j++) {
                System.out.print(coefficients[i][j] + " ");
            }
            System.out.println("| " + constants[i] + " |");
        }
        System.out.println();
    }

    private void printDeterminant(SolutionResult result) {
        System.out.println("Определитель матрицы: det(A) = " + result.getDeterminant());
        System.out.println();
    }

    private void printUpperTriangularMatrix(SolutionResult result) {
        System.out.println("Верхняя треугольная матрица после исключения (расширенная матрица):");

        Double[][] upperAugmented = result.getTriangularMatrix();
        int n = upperAugmented.length;

        for (int i = 0; i < n; i++) {
            System.out.print("| ");
            for (int j = 0; j < n; j++) {
                System.out.print(upperAugmented[i][j] + " ");
            }
            System.out.println("| " + upperAugmented[i][n] + " |");
        }
        System.out.println();
    }

    private void printSolution(SolutionResult result) {
        System.out.println("Вектор решения x:");
        Double[] solution = result.getSolution();
        for (int i = 0; i < solution.length; i++) {
            System.out.println("x" + (i + 1) + " = " + solution[i]);
        }
        System.out.println();
    }

    private void printResidual(SolutionResult result) {
        System.out.println("Вектор невязки r = Ax - b:");
        Double[] residual = result.getResidual();
        double maxResidual = 0;

        for (int i = 0; i < residual.length; i++) {
            System.out.println("r" + (i + 1) + " = " + residual[i]);
            maxResidual = Math.max(maxResidual, Math.abs(residual[i]));
        }
        System.out.println("\nМаксимальная невязка: " + maxResidual);
    }

    private void printVerification(SolutionResult result, MatrixData originalData) {
        System.out.println("\nПроверка результата (сравнение A*x и b):");
        Double[][] originalA = originalData.getCoefficients();
        Double[] originalB = originalData.getConstants();
        Double[] solution = result.getSolution();

        for (int i = 0; i < originalA.length; i++) {
            Double sum = 0.0;
            for (int j = 0; j < originalA.length; j++) {
                sum += originalA[i][j] * solution[j];
            }
            System.out.println("Уравнение " + (i + 1) + ": левая часть = " + sum + ", правая часть = " + originalB[i] + ", разность = " + (sum - originalB[i]));
        }
    }
}
