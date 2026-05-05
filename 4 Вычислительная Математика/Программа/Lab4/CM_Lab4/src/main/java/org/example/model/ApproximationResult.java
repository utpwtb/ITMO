package org.example.model;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ApproximationResult {
    private String functionType;
    private double[] coefficients;
    private double s;
    private double delta;
    private double r2;
    private double pearsonR;
    private double[] yPredicted;
    private double[] residuals;
    private String r2Message;

    public ApproximationResult(String functionType, double[] coefficients) {
        this.functionType = functionType;
        this.coefficients = coefficients;
    }
}
