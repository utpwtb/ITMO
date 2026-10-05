package com.itmo.jmx;

public interface AreaCalculatorMBean {

    double getArea(double r);

    String getFigureDescription();

    void setCurrentR(double r);

    double getCurrentR();

    double getCurrentArea();
}
