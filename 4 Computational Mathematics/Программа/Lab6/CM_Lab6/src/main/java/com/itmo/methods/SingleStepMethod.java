package com.itmo.methods;

import com.itmo.model.SolveResult;
import com.itmo.ode.ODE;

public abstract class SingleStepMethod {

    public abstract double step(ODE ode, double xi, double yi, double h);

    protected abstract int order();

    protected abstract String methodName();

    public SolveResult solve(ODE ode, double x0, double y0,
                             double xn, double h) {
        int n = (int) Math.round((xn - x0) / h);
        double[] x = new double[n + 1];
        double[] y = new double[n + 1];
        x[0] = x0;
        y[0] = y0;

        for (int i = 0; i < n; i++) {
            x[i + 1] = x[i] + h;
            y[i + 1] = step(ode, x[i], y[i], h);
        }

        double rungeErr = rungeError(ode, x0, y0, xn, h);

        return new SolveResult(x, y, rungeErr, methodName(), "runge");
    }

    public double rungeError(ODE ode, double x0, double y0,
                              double xn, double h) {
        int n = (int) Math.round((xn - x0) / h);
        double[] yHalf = solveHalfStep(ode, x0, y0, xn, h);

        double[] yH = new double[n + 1];
        yH[0] = y0;
        double xi = x0;
        for (int i = 0; i < n; i++) {
            yH[i + 1] = step(ode, xi, yH[i], h);
            xi += h;
        }

        double maxErr = 0.0;
        double denom = Math.pow(2, order()) - 1;
        for (int i = 0; i <= n; i++) {
            double diff = Math.abs(yH[i] - yHalf[2 * i]);
            double r = diff / denom;
            if (r > maxErr) {
                maxErr = r;
            }
        }
        return maxErr;
    }

    private double[] solveHalfStep(ODE ode, double x0, double y0,
                                    double xn, double h) {
        double hHalf = h / 2.0;
        int nHalf = (int) Math.round((xn - x0) / hHalf);
        double[] y = new double[nHalf + 1];
        y[0] = y0;
        double xi = x0;
        for (int i = 0; i < nHalf; i++) {
            y[i + 1] = step(ode, xi, y[i], hHalf);
            xi += hHalf;
        }
        return y;
    }
}
