package com.itmo.core.utils.models;

import lombok.Getter;

/**
 * Runge法则计算结果
 */
@Getter
public class RungeResult {
    private final double value;
    private final int n;
    private final double error;
    private final boolean converged;
    private final int iterations;

    public RungeResult(double value, int n, double error, boolean converged, int iterations) {
        this.value = value;
        this.n = n;
        this.error = error;
        this.converged = converged;
        this.iterations = iterations;
    }
}
