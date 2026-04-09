package com.itmo.core.model;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class SystemSolveResult {
    private final double x1;
    private final double x2;
    private final double f1Value;
    private final double f2Value;
    private final int iterations;
    private final boolean converged;
    private final String message;
    @Getter(AccessLevel.NONE)
    private final double[] errors;

    public double[] getErrors() { return errors.clone(); }
}
