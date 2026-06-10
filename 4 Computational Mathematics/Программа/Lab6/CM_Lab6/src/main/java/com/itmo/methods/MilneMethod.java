package com.itmo.methods;

import com.itmo.model.SolveResult;
import com.itmo.ode.ODE;

public class MilneMethod {

    private static final RungeKuttaMethod rk4 = new RungeKuttaMethod();

    public static double[] step(ODE ode, double xi, double h,
                                 double y_im4, double y_im2,
                                 double f_im3, double f_im2, double f_im1) {
        // Predictor
        double yPredict = y_im4
                + (4.0 * h / 3.0) * (2.0 * f_im3 - f_im2 + 2.0 * f_im1);

        // Corrector
        double fPredict = ode.f(xi, yPredict);
        double yCorrect = y_im2
                + (h / 3.0) * (f_im2 + 4.0 * f_im1 + fPredict);

        double fCorrect = ode.f(xi, yCorrect);
        return new double[]{yCorrect, fCorrect};
    }

    public static SolveResult solve(ODE ode, double x0, double y0,
                                     double xn, double h) {
        int n = (int) Math.round((xn - x0) / h);
        double[] x = new double[n + 1];
        double[] y = new double[n + 1];
        double[] f = new double[n + 1];

        x[0] = x0;
        y[0] = y0;
        f[0] = ode.f(x0, y0);

        // Start-up: compute y1, y2, y3 using RK4
        for (int i = 0; i < Math.min(3, n); i++) {
            x[i + 1] = x[i] + h;
            y[i + 1] = rk4.step(ode, x[i], y[i], h);
            f[i + 1] = ode.f(x[i + 1], y[i + 1]);
        }

        // Milne predictor-corrector for the remaining steps
        for (int i = 4; i <= n; i++) {
            x[i] = x[i - 1] + h;
            double[] stepResult = step(ode, x[i], h,
                    y[i - 4], y[i - 2],
                    f[i - 3], f[i - 2], f[i - 1]);
            y[i] = stepResult[0];
            f[i] = stepResult[1];
        }

        double maxErr = exactError(ode, x, y, x0, y0);

        return new SolveResult(x, y, maxErr, "Милн", "exact");
    }

    public static double exactError(ODE ode, double[] x, double[] y,
                                     double x0, double y0) {
        double maxErr = 0.0;
        for (int i = 0; i < x.length; i++) {
            double exact = ode.exact(x[i], x0, y0);
            double diff = Math.abs(exact - y[i]);
            if (diff > maxErr) {
                maxErr = diff;
            }
        }
        return maxErr;
    }
}
