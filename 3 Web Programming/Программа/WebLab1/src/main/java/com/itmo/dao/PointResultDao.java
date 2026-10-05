package com.itmo.dao;

import com.itmo.entity.PointResult;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class PointResultDao {
    private static final List<PointResult> results = new CopyOnWriteArrayList<>();

    public void save(PointResult result) {
        results.add(result);
    }

    public List<PointResult> findAll() {
        return new ArrayList<>(results);
    }

    public void clearAll() {
        results.clear();
    }
}