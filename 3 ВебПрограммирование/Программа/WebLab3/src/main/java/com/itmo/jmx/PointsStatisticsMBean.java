package com.itmo.jmx;

public interface PointsStatisticsMBean {

    long getTotalPoints();

    long getMissedPoints();

    long getHitPoints();

    int getConsecutiveMisses();

    double getHitRate();

    void reset();
}
