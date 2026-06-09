package com.itmo.ode;

public interface ODE {

    double f(double x, double y);

    double exact(double x, double x0, double y0);

    String expression();

    String exactExpression();
}
