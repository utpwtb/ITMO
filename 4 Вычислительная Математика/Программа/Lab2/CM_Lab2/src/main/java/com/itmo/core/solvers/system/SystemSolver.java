package com.itmo.core.solvers.system;

import com.itmo.core.model.SystemSolveResult;
import com.itmo.core.functions.SystemInfo;

public interface SystemSolver {
    SystemSolveResult solve(SystemInfo system, double x1Init, double x2Init, double epsilon);
    String getMethodName();
}
