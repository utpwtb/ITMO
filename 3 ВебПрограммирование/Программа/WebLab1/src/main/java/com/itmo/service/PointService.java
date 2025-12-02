package com.itmo.service;

import com.itmo.dao.PointResultDao;
import com.itmo.entity.PointResult;

import java.time.LocalDateTime;
import java.util.List;

public class PointService {
    private final PointResultDao pointResultDao;

    public PointService() {
        this.pointResultDao = new PointResultDao();
    }

    public boolean validateParameters(double x, double y, double r) {
        boolean validX = x == -5 || x == -4 || x == -3 || x == -2 || x == -1 ||
                x == 0 || x == 1 || x == 2 || x == 3;

        boolean validY = y >= -5 && y <= 3;

        boolean validR = r == 1 || r == 1.5 || r == 2 || r == 2.5 || r == 3;

        return validX && validY && validR;
    }

    public boolean isPointInArea(double x, double y, double r) {
        if (x >= 0 && y <= 0 && x * x + y * y <= (r / 2) * (r / 2)) {
            return true;
        }
        if (x <= 0 && y >= 0 && x >= -r && y <= r) {
            return true;
        }
        if (x >= 0 && y >= 0 && x <= r && y <= r) {
            return true;
        }
        return false;
    }

    public PointResult processPoint(double x, double y, double r) {
        long startTime = System.nanoTime();
        LocalDateTime currentTime = LocalDateTime.now();

        boolean isValid = validateParameters(x, y, r);
        boolean isHit = isValid && isPointInArea(x, y, r);

        long executionTime = (System.nanoTime() - startTime) / 1_000_000;

        PointResult result = new PointResult(x, y, r, isHit, currentTime, executionTime);
        pointResultDao.save(result);

        return result;
    }

    public List<PointResult> getAllResults() {
        return pointResultDao.findAll();
    }

    public void clearAllResults() {
        pointResultDao.clearAll();
    }
}