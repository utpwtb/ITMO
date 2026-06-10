package com.itmo.jmx;

public class AreaCalculator implements AreaCalculatorMBean {

    private static final String DESCRIPTION =
            "Фигура состоит из трёх областей:\n"
                    + "  I четверть (x>=0, y>=0):  прямоугольный треугольник  S1 = R²/2\n"
                    + "  II четверть (x<=0, y>=0):  четверть круга              S2 = πR²/4\n"
                    + "  IV четверть (x>=0, y<=0):  прямоугольник               S3 = R²\n"
                    + "Общая площадь S = R² × (6 + π) / 4 ≈ R² × 2.2854";

    private volatile double currentR = 1.0;

    private static AreaCalculator instance;

    public AreaCalculator() {
        instance = this;
    }

    public static AreaCalculator getInstance() {
        return instance;
    }

    @Override
    public void setCurrentR(double r) {
        this.currentR = r;
    }

    @Override
    public double getCurrentArea() {
        return getArea(currentR);
    }

    @Override
    public double getCurrentR() {
        return currentR;
    }

    @Override
    public double getArea(double r) {
        if (r <= 0) {
            return 0.0;
        }
        return r * r * (6.0 + Math.PI) / 4.0;
    }

    @Override
    public String getFigureDescription() {
        return DESCRIPTION;
    }
}
