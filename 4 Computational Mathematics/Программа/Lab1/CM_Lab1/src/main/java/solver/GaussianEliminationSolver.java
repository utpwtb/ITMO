package solver;

import model.MatrixData;
import model.SolutionResult;

public class GaussianEliminationSolver {
    private int swapCount;

    public SolutionResult solve(MatrixData data) {
        int n = data.getDimension();
        Double[][] a = data.getCoefficients();
        Double[] b = data.getConstants();

        Double[][] augmented = createAugmentedMatrix(a, b, n);

        boolean isSingular = forwardElimination(augmented, n);

        double det = calculateDeterminant(augmented, n);

        Double[] solution = backSubstitution(augmented, n);

        Double[] residual =
                calculateResidual(data.getCoefficients(),
                        solution, data.getConstants(), n);

        return
                new SolutionResult(det, augmented, solution,
                        residual, isSingular || Math.abs(det) != 0);
    }

    private Double[][] createAugmentedMatrix(Double[][] a, Double[] b, Integer n) {
        Double[][] augmented = new Double[n][n + 1];

        for (int i = 0; i < a.length; i++) {
            System.arraycopy(a[i], 0, augmented[i], 0, n);
            augmented[i][n] = b[i];
        }

        return augmented;
    }

    private boolean forwardElimination(Double[][] augmented, int n) {
        swapCount = 0;

        for (int i = 0; i < n; i++) {
            int maxPivotRow = findMaxPivotRow(augmented, n, i);

            if (Math.abs(augmented[maxPivotRow][i]) == 0) {
                return false;
            }

            if (maxPivotRow != i) {
                swapRows(augmented, maxPivotRow, i);
                swapCount++;
            }

            eliminateColumn(augmented, n, i);
        }


        return true;
    }

    private int findMaxPivotRow(Double[][] augmented, int n, int currentRow) {
        int maxRow = currentRow;
        double maxValue = Math.abs(augmented[currentRow][currentRow]);

        for (int i = currentRow + 1; i < n; i++) {
            double currentValue = Math.abs(augmented[i][currentRow]);
            if (currentValue > maxValue) {
                maxValue = currentValue;
                maxRow = i;
            }
        }

        return maxRow;
    }

    private void swapRows(Double[][] augmented, int row1, int row2) {
        Double[] temp = augmented[row1];
        augmented[row1] = augmented[row2];
        augmented[row2] = temp;
    }

    private void eliminateColumn(Double[][] augmented, int n, int currentRow) {
        for (int i = currentRow + 1; i < n; i++) {
            Double factor = augmented[i][currentRow] / augmented[currentRow][currentRow];
            augmented[i][currentRow] = 0.0;
            for (int j = currentRow + 1; j <= n; j++) {
                augmented[i][j] -= factor * augmented[currentRow][j];
            }
        }
    }

    private Double[] backSubstitution(Double[][] upperAugmented, int n) {
        Double[] x = new Double[n];

        x[n - 1] = upperAugmented[n - 1][n] / upperAugmented[n - 1][n - 1];

        //(x_{n-1} 到 x_1)
        for (int i = n - 2; i >= 0; i--) {
            double sum = 0;

            //a_i(i+1)*x_(i+1) + ... + a_in*x_n
            for (int j = i + 1; j < n; j++) {
                sum += upperAugmented[i][j] * x[j];
            }

            //x_i = (b_i - sum) / a_ii
            x[i] = (upperAugmented[i][n] - sum) / upperAugmented[i][i];
        }

        return x;
    }

    private Double[] calculateResidual(Double[][] originalA, Double[] solution,
                                       Double[] originalB, int n) {
        Double[] r = new Double[n];
        for (int i = 0; i < n; i++) {
            double sum = 0;
            for (int j = 0; j < n; j++) {
                sum += originalA[i][j] * solution[j];
            }
            r[i] = sum - originalB[i];
        }
        return r;
    }

    private double calculateDeterminant(Double[][] augmented, int n) {
        double det = 1.0;
        for (int i = 0; i < n; i++) {
            det *= augmented[i][i];
        }
        return (swapCount % 2 == 0) ? det : -det;
    }
}
