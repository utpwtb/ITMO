package com.itmo.methods;

import com.itmo.ode.ODE;

public class RungeKuttaMethod extends SingleStepMethod {

    @Override
    public double step(ODE ode, double xi, double yi, double h) {
        double k1 = h * ode.f(xi, yi);
        double k2 = h * ode.f(xi + h / 2.0, yi + k1 / 2.0);
        double k3 = h * ode.f(xi + h / 2.0, yi + k2 / 2.0);
        double k4 = h * ode.f(xi + h, yi + k3);
        return yi + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0;
    }

    @Override
    protected int order() { return 4; }

    @Override
    protected String methodName() { return "Runge-Kutta 4"; }
}
