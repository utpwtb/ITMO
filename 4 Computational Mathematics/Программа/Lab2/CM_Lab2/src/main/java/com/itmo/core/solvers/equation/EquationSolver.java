package com.itmo.core.solvers.equation;

import com.itmo.core.model.SolveResult;
import com.itmo.core.functions.Function;

public interface EquationSolver {
    SolveResult solve(Function function, Function derivative, Function secondDerivative, double a, double b, double epsilon);
    String getMethodName();
}
