package model;

public class MatrixData {
    private final Integer dimension;
    private final Double[][] coefficients;
    private final Double[] constants;

    public MatrixData(Integer dimension, Double[][] coefficients, Double[] constants) {
        this.dimension = dimension;
        this.coefficients = coefficients;
        this.constants = constants;
    }

    public Double[] getConstants() {
        return constants;
    }

    public Double[][] getCoefficients() {
        return coefficients;
    }

    public Integer getDimension() {
        return dimension;
    }
}
