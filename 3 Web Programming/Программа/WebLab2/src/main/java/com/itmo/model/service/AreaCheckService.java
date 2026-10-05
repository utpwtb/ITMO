package com.itmo.model.service;

import com.itmo.model.pojo.Point;

import java.time.LocalDateTime;

public class AreaCheckService {

    private boolean checkHit(double x, double y, double r) {
        if (x >= 0 && y <= 0 && x * x + y * y <= (r / 2) * (r / 2)) {
            return true;
        }

        if (x <= 0 && y >= 0 && x >= -r && y <= r && y <= x + r) {
            return true;
        }

        if (x >= 0 && y >= 0 && x <= r && y <= r) {
            return true;
        }

        return false;
    }

    public Point createAndCheckPoint(double x, double y, double r) {
        long startTime = System.currentTimeMillis();
        boolean checkHit = checkHit(x, y, r);
        return new Point(x, y, r, checkHit, LocalDateTime.now(), String.valueOf((System.currentTimeMillis() - startTime) / 1_000_000));
    }

}
