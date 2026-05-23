package org.example.model;

public class InterpolationResult {
    private final String methodName;
    private final double x;
    private final double y;
    private final double[][] finiteDiffTable;
    private final int degree;

    public InterpolationResult(String methodName, double x, double y,
                               double[][] finiteDiffTable, int degree) {
        this.methodName = methodName;
        this.x = x;
        this.y = y;
        this.finiteDiffTable = finiteDiffTable;
        this.degree = degree;
    }

    public String getMethodName() { return methodName; }
    public double getX() { return x; }
    public double getY() { return y; }
    public double[][] getFiniteDiffTable() { return finiteDiffTable; }
    public int getDegree() { return degree; }

    @Override
    public String toString() {
        return String.format("%s: f(%.4f) = %.6f (degree=%d)",
                methodName, x, y, degree);
    }
}
