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

    public boolean isEquallySpaced() {
        if (x.length < 2) return true;
        double h = getH();
        for (int i = 1; i < x.length; i++) {
            if (Math.abs((x[i] - x[i - 1]) - h) > 1e-9) return false;
        }
        return true;
    }
}
