package org.example.util;

import org.example.engine.GaussSolver;
import org.example.engine.NewtonSolver;
import org.example.model.InterpolationResult;

public class InterpolationUtils {

    public static InterpolationResult interpolateNewton(double[] x, double[] y,
                                                        double xTarget) {
        int mid = x.length / 2;
        if (xTarget <= x[mid]) {
            return NewtonSolver.interpolateForward(x, y, xTarget);
        } else {
            return NewtonSolver.interpolateBackward(x, y, xTarget);
        }
    }

    public static InterpolationResult interpolateGauss(double[] x, double[] y,
                                                       double xTarget) {
        int c = y.length / 2;
        double q = (xTarget - x[c]) / (x[1] - x[0]);
        if (q >= 0) {
            return GaussSolver.interpolateForward(x, y, xTarget);
        } else {
            return GaussSolver.interpolateBackward(x, y, xTarget);
        }
    }
}
