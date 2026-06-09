package com.itmo.jmx;

import javax.management.Notification;
import javax.management.NotificationBroadcasterSupport;

/**
 * MBean implementation that tracks total points and missed points.
 * Sends a JMX {@link Notification} when the user accumulates 3 consecutive misses.
 *
 * <p>ObjectName: {@code com.itmo:type=PointsStatistics}</p>
 */
public class PointsStatistics
        extends NotificationBroadcasterSupport
        implements PointsStatisticsMBean {

    private long totalPoints;
    private long missedPoints;
    private long hitPoints;
    private int consecutiveMisses;
    private long notificationSequence;

    /** Singleton reference set in constructor for convenient access from managed beans. */
    private static PointsStatistics instance;

    public PointsStatistics() {
        instance = this;
    }

    /** Returns the singleton instance registered in the MBean server. */
    public static PointsStatistics getInstance() {
        return instance;
    }

    // ---------- MBean attributes ----------

    @Override
    public long getTotalPoints() {
        return totalPoints;
    }

    @Override
    public long getMissedPoints() {
        return missedPoints;
    }

    @Override
    public long getHitPoints() {
        return hitPoints;
    }

    @Override
    public int getConsecutiveMisses() {
        return consecutiveMisses;
    }

    @Override
    public double getHitRate() {
        if (totalPoints == 0) {
            return 0.0;
        }
        return (double) hitPoints / totalPoints * 100.0;
    }

    @Override
    public void reset() {
        totalPoints = 0;
        missedPoints = 0;
        hitPoints = 0;
        consecutiveMisses = 0;
    }

    // ---------- Business logic ----------

    /**
     * Called by {@code ResultsBean.addPoint()} every time a point is checked.
     * Updates counters and fires a notification on every third consecutive miss.
     */
    public void recordPoint(boolean hit) {
        totalPoints++;
        if (hit) {
            hitPoints++;
            consecutiveMisses = 0;
        } else {
            missedPoints++;
            consecutiveMisses++;
            if (consecutiveMisses % 3 == 0) {
                Notification notification = new Notification(
                        "consecutive.three.misses",
                        this,
                        ++notificationSequence,
                        System.currentTimeMillis(),
                        "Пользователь совершил " + consecutiveMisses
                                + " промахов подряд (всего точек: " + totalPoints
                                + ", промахов: " + missedPoints + ")"
                );
                sendNotification(notification);
            }
        }
    }
}
