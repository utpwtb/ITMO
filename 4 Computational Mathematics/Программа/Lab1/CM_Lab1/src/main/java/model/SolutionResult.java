package model;

public class SolutionResult {
    private final Double determinant;
    private final Double[][] triangularMatrix;
    private final Double[] solution;
    private final Double[] residual;
    private final boolean isSingular;

    public SolutionResult(Double determinant, Double[][] triangularMatrix, Double[] solution, Double[] residual, boolean isSingular) {
        this.determinant = determinant;
        this.triangularMatrix = triangularMatrix;
        this.solution = solution;
        this.residual = residual;
        this.isSingular = isSingular;
    }

    public Double getDeterminant() {
        return determinant;
    }

    public Double[][] getTriangularMatrix() {
        return triangularMatrix;
    }

    public Double[] getSolution() {
        return solution;
    }

    public Double[] getResidual() {
        return residual;
    }

    public boolean isSingular() {
        return isSingular;
    }
}
