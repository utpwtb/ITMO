package org.example.model;

public class ApproximationResult {
    private String functionType;
    private double[] coefficients;
    private double s;        // sum of squared deviations
    private double delta;    // RMS deviation
    private double r2;       // coefficient of determination
    private double pearsonR; // Pearson correlation coefficient (linear only)
    private double[] yPredicted;
    private double[] residuals;
    private String r2Message;

    public ApproximationResult(String functionType, double[] coefficients) {
        this.functionType = functionType;
        this.coefficients = coefficients;
    }

    public String getFunctionType() { return functionType; }
    public void setFunctionType(String functionType) { this.functionType = functionType; }
    public double[] getCoefficients() { return coefficients; }
    public void setCoefficients(double[] coefficients) { this.coefficients = coefficients; }
    public double getS() { return s; }
    public void setS(double s) { this.s = s; }
    public double getDelta() { return delta; }
    public void setDelta(double delta) { this.delta = delta; }
    public double getR2() { return r2; }
    public void setR2(double r2) { this.r2 = r2; }
    public double getPearsonR() { return pearsonR; }
    public void setPearsonR(double pearsonR) { this.pearsonR = pearsonR; }
    public double[] getYPredicted() { return yPredicted; }
    public void setYPredicted(double[] yPredicted) { this.yPredicted = yPredicted; }
    public double[] getResiduals() { return residuals; }
    public void setResiduals(double[] residuals) { this.residuals = residuals; }
    public String getR2Message() { return r2Message; }
    public void setR2Message(String r2Message) { this.r2Message = r2Message; }

    public String getFormula() {
        StringBuilder sb = new StringBuilder(functionType + ": y = ");
        if (coefficients.length == 2 && functionType.contains("线性")) {
            sb.append(String.format("%.4fx + %.4f", coefficients[0], coefficients[1]));
        } else if (functionType.contains("二次")) {
            sb.append(String.format("%.4f + %.4fx + %.4fx^2", coefficients[0], coefficients[1], coefficients[2]));
        } else if (functionType.contains("三次")) {
            sb.append(String.format("%.4f + %.4fx + %.4fx^2 + %.4fx^3",
                    coefficients[0], coefficients[1], coefficients[2], coefficients[3]));
        } else if (functionType.contains("指数")) {
            sb.append(String.format("%.4fe^(%.4fx)", coefficients[0], coefficients[1]));
        } else if (functionType.contains("对数")) {
            sb.append(String.format("%.4fln(x) + %.4f", coefficients[0], coefficients[1]));
        } else if (functionType.contains("幂")) {
            sb.append(String.format("%.4fx^(%.4f)", coefficients[0], coefficients[1]));
        }
        return sb.toString();
    }
}
