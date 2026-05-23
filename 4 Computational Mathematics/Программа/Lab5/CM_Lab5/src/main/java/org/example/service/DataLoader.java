package org.example.service;

import org.example.model.InputData;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class DataLoader {

    public static InputData fromArrays(double[] x, double[] y) {
        return new InputData(x, y, "Manual input");
    }

    public static InputData fromFile(String filePath) throws IOException {
        List<Double> xList = new ArrayList<>();
        List<Double> yList = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue;
                String[] parts = line.split("[,\\s]+");
                if (parts.length >= 2) {
                    xList.add(Double.parseDouble(parts[0]));
                    yList.add(Double.parseDouble(parts[1]));
                }
            }
        }

        double[] x = xList.stream().mapToDouble(Double::doubleValue).toArray();
        double[] y = yList.stream().mapToDouble(Double::doubleValue).toArray();
        return new InputData(x, y, "File: " + filePath);
    }

    public static InputData fromFunction(Function<Double, Double> func,
                                         double a, double b, int n) {
        double[] x = new double[n];
        double[] y = new double[n];
        double h = (b - a) / (n - 1);
        for (int i = 0; i < n; i++) {
            x[i] = a + i * h;
            y[i] = func.apply(x[i]);
        }
        return new InputData(x, y, "Function on [" + a + ", " + b + "], n=" + n);
    }
}
