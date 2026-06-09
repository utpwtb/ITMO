package com.itmo.ode;

/**
 * y' = x + y
 * Exact solution: y = -x - 1 + (y0 + x0 + 1) * e^(x - x0)
 */
public class ODE2 implements ODE {

    @Override
    public double f(double x, double y) {
        return x + y;
    }

    @Override
    public double exact(double x, double x0, double y0) {
        double C = y0 + x0 + 1.0;
        return -x - 1.0 + C * Math.exp(x - x0);
    }

    @Override
    public String expression() {
        return "y' = x + y";
    }

    @Override
    public String exactExpression() {
        return "y = -x - 1 + (y₀ + x₀ + 1) · e^(x - x₀)";
    }
}
