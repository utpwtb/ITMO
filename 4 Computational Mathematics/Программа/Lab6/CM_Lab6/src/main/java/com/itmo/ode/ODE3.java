package com.itmo.ode;

/**
 * y' = -2xy
 * Exact solution: y = y0 * e^(-x^2 + x0^2)
 */
public class ODE3 implements ODE {

    @Override
    public double f(double x, double y) {
        return -2.0 * x * y;
    }

    @Override
    public double exact(double x, double x0, double y0) {
        return y0 * Math.exp(-x * x + x0 * x0);
    }

    @Override
    public String expression() {
        return "y' = -2xy";
    }

    @Override
    public String exactExpression() {
        return "y = y₀ · e^(-x² + x₀²)";
    }
}
