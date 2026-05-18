package com.itmo.gui.utils;

import com.itmo.core.functions.SystemInfo;

public final class SystemSolutionVerifier {
    private SystemSolutionVerifier() {}

    public static double[] verify(SystemInfo system, double x1, double x2) {
        double f1Val = system.getF1().evaluate(x1, x2);
        double f2Val = system.getF2().evaluate(x1, x2);
        return new double[]{f1Val, f2Val};
    }
}
