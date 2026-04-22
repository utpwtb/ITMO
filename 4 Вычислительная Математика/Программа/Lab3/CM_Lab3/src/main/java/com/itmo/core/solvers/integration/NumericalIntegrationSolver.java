package com.itmo.core.solvers.integration;

import com.itmo.core.functions.Function;

public interface NumericalIntegrationSolver {
    double integrate(Function function, double a, double b, int n);
    String getMethodName();
}
