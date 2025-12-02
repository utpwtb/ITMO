package com.itmo.model.dao;

import java.util.ArrayList;
import java.util.List;

import com.itmo.model.pojo.Point;

public class PointDao {
    private final List<Point> points = new ArrayList<>();

    
    public void addPoint(Point point) {
        points.add(point);
    }

    public List<Point> getPoints() {
        return points;
    }

}
