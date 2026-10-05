package com.itmo.jmx;

import javax.management.Notification;
import javax.management.NotificationBroadcasterSupport;

public class PointsStatistics
        extends NotificationBroadcasterSupport
        implements PointsStatisticsMBean {

    private long totalPoints;
    private long missedPoints;
    private long hitPoints;
    private int consecutiveMisses;
    private long notificationSequence;

    private static PointsStatistics instance;

    public PointsStatistics() {
        instance = this;
    }

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
