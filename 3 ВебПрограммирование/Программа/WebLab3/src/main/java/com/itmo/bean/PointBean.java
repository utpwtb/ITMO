package com.itmo.bean;

import com.itmo.model.pojo.Point;
import lombok.Getter;
import lombok.Setter;

import javax.faces.bean.ManagedBean;
import javax.faces.bean.ManagedProperty;
import javax.faces.bean.RequestScoped;
import java.time.LocalDateTime;

@Setter
@Getter
@ManagedBean(name = "pointBean")
@RequestScoped
public class PointBean {
    @Getter
    private Double x;
    private Double y;
    private Double r;
    private SubmitSource submitSource;

    @ManagedProperty("#{resultsBean}")
    private ResultsBean resultsBean;

    public enum SubmitSource {
        FORM,
        SVG
    }

    public String checkPoint() {
        if (x == null || y == null || r == null) {
            return null;
        }

        if (y < -3 || y > 5 || r < 1 || r > 4) {
            return null;
        }

        //ПРОБЛЕМА: конкатенация String в цикле
        /*String debugLog = "";
        for (int i = 0; i < 50000; i++) {
            debugLog += "Point[" + i + "]=(" + x + "," + y + "," + r + ") ";
        }*/

        StringBuilder debugLog = new StringBuilder();
        for (int i = 0; i < 50000; i++) {
            debugLog.append("Point[").append(i).append("]=(")
                    .append(x).append(",").append(y).append(",").append(r).append(") ");
        }


        long startTime = System.currentTimeMillis();
        boolean hit = checkHit(x, y, r);
        long executionTime = System.currentTimeMillis() - startTime;

        Point point = new Point();
        point.setX(x);
        point.setY(y);
        point.setR(r);
        point.setHit(hit);
        point.setCurrentTime(LocalDateTime.now());
        point.setExecutionTime(executionTime);

        resultsBean.addPoint(point);

        reset();
        return null;
    }

    private boolean checkHit(double x, double y, double r) {
        if (x >= 0 && y >= 0 && x + y <= r) {
            return true;
        }
        if (x <= 0 && y >= 0 && x * x + y * y <= r * r) {
            return true;
        }
        if (x >= 0 && y <= 0 && x <= r && y >= -r) {
            return true;
        }
        return false;
    }

    public void reset() {
        x = null;
        y = null;
        r = null;
    }
}
