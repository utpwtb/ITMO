package com.itmo.core.solvers.system.utils;

public final class ConvergenceCheckResult {
    public final double dphi1dx;
    public final double dphi1dy;
    public final double dphi2dx;
    public final double dphi2dy;
    public final double jacobianNorm;
    public final boolean conditionMet;

    public ConvergenceCheckResult(double dphi1dx, double dphi1dy,
                                   double dphi2dx, double dphi2dy) {
        this.dphi1dx = dphi1dx;
        this.dphi1dy = dphi1dy;
        this.dphi2dx = dphi2dx;
        this.dphi2dy = dphi2dy;
        double row1Sum = Math.abs(dphi1dx) + Math.abs(dphi1dy);
        double row2Sum = Math.abs(dphi2dx) + Math.abs(dphi2dy);
        this.jacobianNorm = Math.max(row1Sum, row2Sum);
        this.conditionMet = jacobianNorm < 1.0;
    }
}
