package org.example.gui;

import org.example.model.InputData;
import org.example.model.InterpolationResult;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.ArrayList;
import java.util.List;

public class ChartPanel extends JPanel {

    private InputData data;
    private final List<InterpolationResult> results = new ArrayList<>();
    private double xTarget1, xTarget2;

    private static final Color[] CURVE_COLORS = {
            new Color(220, 50, 50),   // red
            new Color(50, 100, 220),  // blue
            new Color(50, 160, 50),   // green
            new Color(180, 50, 180),  // purple
            new Color(220, 150, 30),  // orange
            new Color(30, 160, 160),  // teal
    };

    private static final int PADDING = 60;
    private static final int LEGEND_X = 70;

    public ChartPanel() {
        setBackground(Color.WHITE);
        setPreferredSize(new Dimension(550, 480));
    }

    public void setData(InputData data, double xTarget1, double xTarget2,
                        List<InterpolationResult> results) {
        this.data = data;
        this.xTarget1 = xTarget1;
        this.xTarget2 = xTarget2;
        this.results.clear();
        this.results.addAll(results);
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                RenderingHints.VALUE_ANTIALIAS_ON);

        if (data == null || data.size() == 0) {
            g2.drawString("Нет данных для отображения", getWidth() / 2 - 55,
                    getHeight() / 2);
            return;
        }

        double[] x = data.getX();
        double[] y = data.getY();

        double xMin = x[0];
        double xMax = x[x.length - 1];
        double yMin = y[0];
        double yMax = y[0];
        for (double v : y) {
            if (v < yMin) yMin = v;
            if (v > yMax) yMax = v;
        }

        // Include target points in range
        double xRange = xMax - xMin;
        xMin -= xRange * 0.1;
        xMax += xRange * 0.1;
        double yRange = yMax - yMin;
        yMin -= yRange * 0.15;
        yMax += yRange * 0.15;

        int plotW = getWidth() - 2 * PADDING;
        int plotH = getHeight() - 2 * PADDING;

        // Draw axes
        g2.setColor(Color.BLACK);
        g2.setStroke(new BasicStroke(1.5f));
        g2.drawLine(PADDING, getHeight() - PADDING,
                getWidth() - PADDING, getHeight() - PADDING);
        g2.drawLine(PADDING, PADDING, PADDING, getHeight() - PADDING);

        // Draw grid
        g2.setStroke(new BasicStroke(0.5f, BasicStroke.CAP_BUTT,
                BasicStroke.JOIN_MITER, 10, new float[]{4, 4}, 0));
        g2.setColor(new Color(200, 200, 200));
        for (int i = 0; i <= 5; i++) {
            int gy = getHeight() - PADDING - i * plotH / 5;
            g2.drawLine(PADDING, gy, getWidth() - PADDING, gy);
            int gx = PADDING + i * plotW / 5;
            g2.drawLine(gx, PADDING, gx, getHeight() - PADDING);
        }

        // Draw axis labels
        g2.setColor(Color.BLACK);
        g2.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        for (int i = 0; i <= 5; i++) {
            double val = xMin + (xMax - xMin) * i / 5;
            int gx = PADDING + i * plotW / 5;
            g2.drawString(String.format("%.2f", val), gx - 12,
                    getHeight() - PADDING + 15);
            val = yMin + (yMax - yMin) * (5 - i) / 5;
            int gy = getHeight() - PADDING - i * plotH / 5;
            g2.drawString(String.format("%.2f", val), 5, gy + 4);
        }

        // Draw interpolation curves
        g2.setStroke(new BasicStroke(1.8f));
        int colorIdx = 0;
        for (InterpolationResult r : results) {
            g2.setColor(CURVE_COLORS[colorIdx % CURVE_COLORS.length]);
            Path2D path = new Path2D.Double();
            boolean started = false;

            for (int i = 0; i <= 300; i++) {
                double xi = xMin + (xMax - xMin) * i / 300.0;
                // Compute interpolated value using the same engine
                double yi = evaluateMethod(x, y, xi, r.getMethodName());
                double px = PADDING + (xi - xMin) / (xMax - xMin) * plotW;
                double py = getHeight() - PADDING
                        - (yi - yMin) / (yMax - yMin) * plotH;

                if (!started) {
                    path.moveTo(px, py);
                    started = true;
                } else {
                    path.lineTo(px, py);
                }
            }
            g2.draw(path);
            colorIdx++;
        }

        // Draw original nodes
        g2.setColor(new Color(20, 20, 20));
        for (int i = 0; i < x.length; i++) {
            double px = PADDING + (x[i] - xMin) / (xMax - xMin) * plotW;
            double py = getHeight() - PADDING
                    - (y[i] - yMin) / (yMax - yMin) * plotH;
            Ellipse2D node = new Ellipse2D.Double(px - 5, py - 5, 10, 10);
            g2.fill(node);
            g2.setColor(Color.WHITE);
            g2.fill(new Ellipse2D.Double(px - 2.5, py - 2.5, 5, 5));
            g2.setColor(new Color(20, 20, 20));
        }

        // Draw target points X1, X2
        g2.setColor(new Color(200, 30, 30));
        double[] targets = {xTarget1, xTarget2};
        for (double xt : targets) {
            if (xt < xMin || xt > xMax) continue;
            double yt = evaluateMethod(x, y, xt, "");
            double px = PADDING + (xt - xMin) / (xMax - xMin) * plotW;
            double py = getHeight() - PADDING
                    - (yt - yMin) / (yMax - yMin) * plotH;
            Ellipse2D target = new Ellipse2D.Double(px - 6, py - 6, 12, 12);
            g2.setStroke(new BasicStroke(2.5f));
            g2.draw(target);
            g2.drawLine((int) px - 3, (int) py, (int) px + 3, (int) py);
            g2.drawLine((int) px, (int) py - 3, (int) px, (int) py + 3);
            g2.setStroke(new BasicStroke(1.8f));
        }

        // Legend
        int legendY = PADDING + 12;
        g2.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        g2.setColor(new Color(20, 20, 20));
        g2.drawString("Узлы", LEGEND_X, legendY);
        legendY += 15;
        for (int i = 0; i < results.size(); i++) {
            g2.setColor(CURVE_COLORS[i % CURVE_COLORS.length]);
            g2.drawString(results.get(i).getMethodName(), LEGEND_X, legendY);
            legendY += 15;
        }
        g2.setColor(new Color(200, 30, 30));
        g2.drawString("X1, X2", LEGEND_X, legendY);
    }

    /** Quick interpolation using Lagrange for chart drawing */
    private double evaluateMethod(double[] x, double[] y, double xi,
                                  String methodName) {
        // Use Lagrange for all chart evaluation since it's simplest
        double result = 0.0;
        for (int i = 0; i < x.length; i++) {
            double term = y[i];
            for (int j = 0; j < x.length; j++) {
                if (i != j) {
                    term *= (xi - x[j]) / (x[i] - x[j]);
                }
            }
            result += term;
        }
        return result;
    }
}
