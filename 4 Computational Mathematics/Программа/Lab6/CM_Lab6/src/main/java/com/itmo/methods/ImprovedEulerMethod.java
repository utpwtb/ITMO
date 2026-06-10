package com.itmo.methods;

import com.itmo.ode.ODE;

public class ImprovedEulerMethod extends SingleStepMethod {

    @Override
    public double step(ODE ode, double xi, double yi, double h) {
        double f_xi_yi = ode.f(xi, yi);
        double yTilde = yi + h * f_xi_yi;
        return yi + (h / 2.0) * (f_xi_yi + ode.f(xi + h, yTilde));
    }

    @Override
    protected int order() { return 2; }

    @Override
    protected String methodName() { return "Модифицированный Эйлер"; }
}
