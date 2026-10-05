package com.itmo.bean;

import com.itmo.jmx.AreaCalculator;
import com.itmo.jmx.PointsStatistics;
import com.itmo.model.dao.PointDao;
import com.itmo.model.pojo.Point;

import javax.annotation.PostConstruct;
import javax.faces.bean.ApplicationScoped;
import javax.faces.bean.ManagedBean;
import javax.ejb.EJB;
import java.util.ArrayList;
import java.util.List;

@ManagedBean(name = "resultsBean")
@ApplicationScoped
public class ResultsBean {

    private List<Point> points;

    @EJB
    private PointDao pointDao;

    @PostConstruct
    public void init() {
        points = new ArrayList<>();
        loadPoints();
    }

    private void loadPoints() {
        points = pointDao.getAll();
    }

    public List<Point> getPoints() {
        return points;
    }

    public void clearResults() {
        pointDao.deleteAll();
        points.clear();
    }

    public void addPoint(Point point) {
        pointDao.save(point);
        points.add(0, point);

        // Notify PointsStatistics MBean
        PointsStatistics stats = PointsStatistics.getInstance();
        if (stats != null) {
            stats.recordPoint(point.getHit());
        }

        // Update AreaCalculator MBean with the current R value
        AreaCalculator areaCalc = AreaCalculator.getInstance();
        if (areaCalc != null) {
            areaCalc.setCurrentR(point.getR());
        }
    }
}
