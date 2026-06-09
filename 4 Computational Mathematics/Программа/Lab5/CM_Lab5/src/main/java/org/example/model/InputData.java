package org.example.model;

public class InputData {
    private double[] x;
    private double[] y;
    private String sourceDescription;

    public InputData(double[] x, double[] y, String sourceDescription) {
        this.x = x;
        this.y = y;
        this.sourceDescription = sourceDescription;
    }

    public double[] getX() { return x; }
    public double[] getY() { return y; }
    public String getSourceDescription() { return sourceDescription; }

    public int size() { return x.length; }

    public double getH() {
        if (x.length < 2) return 0;
        return x[1] - x[0];
    }

}
