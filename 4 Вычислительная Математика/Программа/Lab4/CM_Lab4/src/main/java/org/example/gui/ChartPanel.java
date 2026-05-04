package org.example.gui;

import org.example.model.ApproximationResult;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.List;

public class ChartPanel extends JPanel {

    private List<Double> xData;
    private List<Double> yData;
    private List<ApproximationResult> results;

    private static final Color[] COLORS = {
            Color.RED, Color.BLUE, new Color(0, 150, 0),
            Color.MAGENTA, new Color(139, 69, 19), Color.ORANGE
    };

    private static final int PADDING = 60;

    public ChartPanel() {
        setBackground(Color.WHITE);
    }

    public void setData(List<Double> xData, List<Double> yData, List<ApproximationResult> results) {
        this.xData = xData;
        this.yData = yData;
        this.results = results;
        repaint();
    }

    public void clear() {
        this.xData = null;
        this.yData = null;
        this.results = null;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        if (xData == null || xData.isEmpty()) {
            g2.setColor(Color.GRAY);
            g2.drawString("暂无数据，请先输入数据并点击计算", getWidth() / 2 - 100, getHeight() / 2);
            return;
        }

        double minX = xData.stream().mapToDouble(Double::doubleValue).min().orElse(0);
        double maxX = xData.stream().mapToDouble(Double::doubleValue).max().orElse(1);
        double minY = yData.stream().mapToDouble(Double::doubleValue).min().orElse(0);
        double maxY = yData.stream().mapToDouble(Double::doubleValue).max().orElse(1);

        if (results != null) {
            for (ApproximationResult r : results) {
                double[] yp = r.getYPredicted();
                if (yp != null) {
                    for (double v : yp) {
                        minY = Math.min(minY, v);
                        maxY = Math.max(maxY, v);
                    }
                }
            }
        }

        double xRange = maxX - minX;
        double yRange = maxY - minY;
        if (xRange == 0) xRange = 1;
        if (yRange == 0) yRange = 1;

        double xMargin = xRange * 0.15;
        double yMargin = yRange * 0.15;
        minX -= xMargin; maxX += xMargin;
        minY -= yMargin; maxY += yMargin;
        double xSpan = maxX - minX;
        double ySpan = maxY - minY;

        final int w = getWidth(), hgt = getHeight();
        final double scaleX = (w - 2 * PADDING) / xSpan;
        final double scaleY = (hgt - 2 * PADDING) / ySpan;
        final double _minX = minX, _minY = minY;

        // Draw axes
        g2.setColor(Color.BLACK);
        g2.setStroke(new BasicStroke(2));
        g2.drawLine(PADDING, hgt - PADDING, w - PADDING, hgt - PADDING); // X axis
        g2.drawLine(PADDING, PADDING, PADDING, hgt - PADDING); // Y axis

        // Draw grid
        g2.setColor(new Color(220, 220, 220));
        g2.setStroke(new BasicStroke(1));
        int gridLines = 10;
        for (int i = 0; i <= gridLines; i++) {
            int x = PADDING + i * (w - 2 * PADDING) / gridLines;
            int y = PADDING + i * (hgt - 2 * PADDING) / gridLines;
            g2.drawLine(x, PADDING, x, hgt - PADDING);
            g2.drawLine(PADDING, y, w - PADDING, y);
        }

        // Draw tick labels
        g2.setColor(Color.BLACK);
        g2.setFont(new Font("Consolas", Font.PLAIN, 10));
        for (int i = 0; i <= gridLines; i++) {
            double xVal = minX + i * xSpan / gridLines;
            double yVal = maxY - i * ySpan / gridLines;
            String xStr = String.format("%.2f", xVal);
            String yStr = String.format("%.2f", yVal);
            int tx = (int) (PADDING + (xVal - _minX) * scaleX);
            int ty = (int) (hgt - PADDING - (yVal - _minY) * scaleY);
            g2.drawString(xStr, tx - 15, hgt - PADDING + 18);
            g2.drawString(yStr, PADDING - 55, ty + 5);
        }

        // Draw axis labels
        g2.setFont(new Font("Microsoft YaHei", Font.BOLD, 13));
        g2.drawString("X", w - PADDING + 10, hgt - PADDING + 5);
        g2.drawString("Y", PADDING - 5, PADDING - 10);

        // Draw fit curves
        if (results != null) {
            for (int idx = 0; idx < results.size(); idx++) {
                ApproximationResult r = results.get(idx);
                if (r.getDelta() >= Double.MAX_VALUE) continue;

                g2.setColor(COLORS[idx % COLORS.length]);
                g2.setStroke(new BasicStroke(2));

                Path2D.Double path = new Path2D.Double();
                int numPts = 500;
                for (int i = 0; i <= numPts; i++) {
                    double xp = minX + i * xSpan / numPts;
                    double yp = r.getYPredicted()[0]; // fallback
                    double[] yPred = r.getYPredicted();
                    if (yPred != null && xData != null) {
                        // Interpolate using the function directly for smooth curves
                        double[] c = r.getCoefficients();
                        switch (r.getFunctionType()) {
                            case "线性函数":
                                yp = c[0] * xp + c[1]; break;
                            case "二次多项式":
                                yp = c[0] + c[1] * xp + c[2] * xp * xp; break;
                            case "三次多项式":
                                yp = c[0] + c[1] * xp + c[2] * xp * xp + c[3] * xp * xp * xp; break;
                            case "指数函数":
                                yp = c[0] * Math.exp(c[1] * xp); break;
                            case "对数函数":
                                yp = xp > 0 ? c[0] * Math.log(xp) + c[1] : c[1]; break;
                            case "幂函数":
                                yp = xp > 0 ? c[0] * Math.pow(xp, c[1]) : 0; break;
                        }
                    }
                    int px = (int) (PADDING + (xp - _minX) * scaleX);
                    int py = (int) (hgt - PADDING - (yp - _minY) * scaleY);
                    if (i == 0) path.moveTo(px, py);
                    else path.lineTo(px, py);
                }
                g2.draw(path);
            }
        }

        // Draw data points
        g2.setColor(Color.BLACK);
        for (int i = 0; i < xData.size(); i++) {
            double xi = xData.get(i), yi = yData.get(i);
            int px = (int) (PADDING + (xi - _minX) * scaleX);
            int py = (int) (hgt - PADDING - (yi - _minY) * scaleY);
            Ellipse2D.Double dot = new Ellipse2D.Double(px - 4, py - 4, 8, 8);
            g2.fill(dot);
        }

        // Draw legend
        if (results != null) {
            int legendX = w - 220;
            int legendY = PADDING + 5;
            g2.setFont(new Font("Microsoft YaHei", Font.PLAIN, 11));
            g2.setColor(new Color(255, 255, 255, 200));
            g2.fillRect(legendX - 5, legendY - 5, 210, 18 * (results.size() + 1) + 15);
            g2.setColor(Color.BLACK);
            g2.drawRect(legendX - 5, legendY - 5, 210, 18 * (results.size() + 1) + 15);

            g2.fillOval(legendX, legendY, 8, 8);
            g2.drawString("原始数据", legendX + 15, legendY + 8);
            legendY += 18;

            for (int idx = 0; idx < results.size(); idx++) {
                ApproximationResult r = results.get(idx);
                if (r.getDelta() >= Double.MAX_VALUE) continue;
                g2.setColor(COLORS[idx % COLORS.length]);
                g2.fillOval(legendX, legendY, 8, 8);
                g2.setColor(Color.BLACK);
                g2.drawString(r.getFunctionType(), legendX + 15, legendY + 8);
                legendY += 18;
            }
        }
    }
}
