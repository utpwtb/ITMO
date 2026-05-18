package org.example.service;

import org.example.engine.LSMSolver;
import org.example.model.ApproximationResult;

import java.util.List;

public class ApproximationService {

    private ApproximationService() {}

    public static String getR2Message(double r2) {
        if (r2 >= 0.95) return "Высокая точность (R² ≥ 0.95)";
        else if (r2 >= 0.75) return "Хорошая точность (0.75 ≤ R² < 0.95)";
        else if (r2 >= 0.5) return "Слабая аппроксимация (0.5 ≤ R² < 0.75)";
        else return "Недостаточная точность (R² < 0.5)";
    }

    public static String getFormula(ApproximationResult r) {
        StringBuilder sb = new StringBuilder(r.getFunctionType());
        sb.append(": y = ");
        double[] c = r.getCoefficients();
        String type = r.getFunctionType();

        if (type.contains("Линейная")) {
            sb.append(String.format("%.4fx + %.4f", c[0], c[1]));
        } else if (type.contains("Квадрати")) {
            sb.append(String.format("%.4f + %.4fx + %.4fx²", c[0], c[1], c[2]));
        } else if (type.contains("Кубический")) {
            sb.append(String.format("%.4f + %.4fx + %.4fx² + %.4fx³",
                    c[0], c[1], c[2], c[3]));
        } else if (type.contains("Экспонен")) {
            sb.append(String.format("%.4fe^(%.4fx)", c[0], c[1]));
        } else if (type.contains("Логариф")) {
            sb.append(String.format("%.4fln(x) + %.4f", c[0], c[1]));
        } else if (type.contains("Степен")) {
            sb.append(String.format("%.4fx^(%.4f)", c[0], c[1]));
        }
        return sb.toString();
    }

    public static List<ApproximationResult> computeAll(List<Double> x, List<Double> y) {
        List<ApproximationResult> results = List.of(
                LSMSolver.linear(x, y),
                LSMSolver.quadratic(x, y),
                LSMSolver.cubic(x, y),
                LSMSolver.exponential(x, y),
                LSMSolver.logarithmic(x, y),
                LSMSolver.power(x, y)
        );

        for (ApproximationResult r : results) {
            if (r.getR2Message() == null) {
                r.setR2Message(getR2Message(r.getR2()));
            }
        }

        return results;
    }
}
