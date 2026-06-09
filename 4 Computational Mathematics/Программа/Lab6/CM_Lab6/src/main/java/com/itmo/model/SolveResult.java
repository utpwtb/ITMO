package com.itmo.model;

/**
 * Holds the result of an ODE numerical solution.
 */
public class SolveResult {

    private final double[] x;
    private final double[] y;
    private final double error;
    private final String methodName;
    private final String errorMethod; // "runge" or "exact"

    public SolveResult(double[] x, double[] y, double error,
                       String methodName, String errorMethod) {
        this.x = x;
        this.y = y;
        this.error = error;
        this.methodName = methodName;
        this.errorMethod = errorMethod;
    }

    public double[] getX() { return x; }
    public double[] getY() { return y; }
    public double getError() { return error; }
    public String getMethodName() { return methodName; }
    public String getErrorMethod() { return errorMethod; }
}
