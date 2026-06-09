package org.example.engine;

public class FiniteDifferenceTable {

    public static double[][] build(double[] y) {
        int n = y.length;
        double[][] table = new double[n][n];
        for (int i = 0; i < n; i++) {
            table[i][0] = y[i];
        }
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < n - j; i++) {
                table[i][j] = table[i + 1][j - 1] - table[i][j - 1];
            }
        }
        return table;
    }
}
