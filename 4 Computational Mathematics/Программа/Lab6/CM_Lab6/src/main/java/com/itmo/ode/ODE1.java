package com.itmo.ode;

/**
 * y' = y
 * Exact solution: y = y0 * e^(x - x0)
 */
public class ODE1 implements ODE {

    @Override
    public double f(double x, double y) {
        return y;
    }

    @Override
    public double exact(double x, double x0, double y0) {
        return y0 * Math.exp(x - x0);
    }

    @Override
    public String expression() {
        return "y' = y";
    }

    @Override
    public String exactExpression() {
        return "y = y₀ · e^(x - x₀)";
    }
}
