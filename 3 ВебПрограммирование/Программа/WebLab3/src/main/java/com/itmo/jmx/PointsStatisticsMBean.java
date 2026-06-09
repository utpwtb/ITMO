package com.itmo.jmx;

/**
 * MBean interface for tracking point-checking statistics.
 * Counts total points, missed (not hitting the target area) points,
 * and fires JMX Notifications when 3 consecutive misses occur.
 */
public interface PointsStatisticsMBean {

    /** Total number of points checked since application start (or last reset). */
    long getTotalPoints();

    /** Number of points that did NOT fall into the target area. */
    long getMissedPoints();

    /** Number of points that DID fall into the target area. */
    long getHitPoints();

    /** Current streak of consecutive misses (resets to 0 on a hit). */
    int getConsecutiveMisses();

    /** Hit rate as a percentage (0.0 – 100.0). */
    double getHitRate();

    /** Reset all counters to zero. */
    void reset();
}
