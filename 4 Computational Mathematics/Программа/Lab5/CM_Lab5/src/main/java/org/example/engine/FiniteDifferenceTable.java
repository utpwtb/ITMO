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

    public static double[][] buildCentral(double[] y) {
        int n = y.length;
        double[][] ft = build(y);

        // For central difference table, reorganize around the middle index
        int center = n / 2;
        double[][] central = new double[n][n];

        // Column 0: y values with central index at row center
        for (int i = 0; i < n; i++) {
            central[i][0] = y[i];
        }

        // For subsequent columns, fill in the central difference pattern
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < n - j; i++) {
                central[i][j] = ft[i][j];
            }
        }

        return central;
    }
}
