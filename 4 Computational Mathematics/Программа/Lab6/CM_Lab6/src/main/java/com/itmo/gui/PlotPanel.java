package com.itmo.gui;

import com.itmo.model.SolveResult;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.List;

/**
 * Plots exact and approximate solution curves (bottom-right area).
 */
public class PlotPanel extends JPanel {

    private static final Color[] COLORS = {
        new Color(220, 50, 50),   // red - Euler
        new Color(50, 100, 220),  // blue - RK4
        new Color(50, 160, 50),   // green - Milne
        new Color(0, 0, 0),       // black - exact
    };

    private static final Stroke DASHED = new BasicStroke(1.5f,
            BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL,
            0, new float[]{6, 4}, 0);
    private static final Stroke SOLID = new BasicStroke(2f);

    private final List<SolveResult> results;
    private final double[] exactX;
    private final double[] exactY;

    private double xMin, xMax, yMin, yMax;

    public PlotPanel(List<SolveResult> results, double[] exactX, double[] exactY) {
        this.results = results;
        this.exactX = exactX;
        this.exactY = exactY;
        setBorder(BorderFactory.createTitledBorder("Plot"));
        setPreferredSize(new Dimension(450, 450));
        computeBounds();
    }

    public PlotPanel() {
        this.results = null;
        this.exactX = null;
        this.exactY = null;
        setBorder(BorderFactory.createTitledBorder("Plot"));
        setPreferredSize(new Dimension(450, 450));
    }

    private void computeBounds() {
        xMin = exactX[0];
        xMax = exactX[exactX.length - 1];
        yMin = exactY[0];
        yMax = exactY[0];
        for (double v : exactY) {
            if (v < yMin) yMin = v;
            if (v > yMax) yMax = v;
        }
        for (SolveResult r : results) {
            for (double v : r.getY()) {
                if (v < yMin) yMin = v;
                if (v > yMax) yMax = v;
            }
        }
        double yPad = (yMax - yMin) * 0.1;
        if (yPad < 0.01) yPad = 0.5;
        yMin -= yPad;
        yMax += yPad;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (results == null || exactX == null) {
            g.drawString("Press 'Compute' to display plot", 30, 30);
            return;
        }
        computeBounds();

        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int pad = 50;
        int w = getWidth() - 2 * pad;
        int h = getHeight() - 2 * pad;

        double xRange = xMax - xMin;
        double yRange = yMax - yMin;

        // Background
        g2.setColor(Color.WHITE);
        g2.fillRect(pad, pad, w, h);

        // Grid
        g2.setColor(new Color(230, 230, 230));
        g2.setStroke(new BasicStroke(0.5f));
        for (int i = 0; i <= 5; i++) {
            int gy = pad + i * h / 5;
            g2.drawLine(pad, gy, pad + w, gy);
            int gx = pad + i * w / 5;
            g2.drawLine(gx, pad, gx, pad + h);
        }

        // Axes
        g2.setColor(Color.BLACK);
        g2.setStroke(new BasicStroke(1f));
        g2.drawRect(pad, pad, w, h);

        // Tick labels
        g2.setFont(new Font("SansSerif", Font.PLAIN, 9));
        for (int i = 0; i <= 5; i++) {
            double xv = xMin + xRange * i / 5.0;
            String label = String.format("%.2f", xv);
            int sx = (int) (pad + (xv - xMin) / xRange * w);
            g2.drawString(label, sx - 15, pad + h + 15);

            double yv = yMin + yRange * i / 5.0;
            label = String.format("%.2f", yv);
            int sy = (int) (pad + h - (yv - yMin) / yRange * h);
            g2.drawString(label, 2, sy + 4);
        }

        // Exact solution (black, dashed)
        g2.setColor(COLORS[3]);
        g2.setStroke(DASHED);
        Path2D exactPath = new Path2D.Double();
        exactPath.moveTo(
                pad + (exactX[0] - xMin) / xRange * w,
                pad + h - (exactY[0] - yMin) / yRange * h);
        for (int i = 1; i < exactX.length; i++) {
            exactPath.lineTo(
                    pad + (exactX[i] - xMin) / xRange * w,
                    pad + h - (exactY[i] - yMin) / yRange * h);
        }
        g2.draw(exactPath);

        // Method results
        for (int m = 0; m < results.size(); m++) {
            SolveResult r = results.get(m);
            g2.setColor(COLORS[m % 3]);
            g2.setStroke(SOLID);

            double[] rx = r.getX();
            double[] ry = r.getY();

            Path2D path = new Path2D.Double();
            path.moveTo(
                    pad + (rx[0] - xMin) / xRange * w,
                    pad + h - (ry[0] - yMin) / yRange * h);
            for (int i = 1; i < rx.length; i++) {
                path.lineTo(
                        pad + (rx[i] - xMin) / xRange * w,
                        pad + h - (ry[i] - yMin) / yRange * h);
            }
            g2.draw(path);

            // Points
            double dotR = 3;
            for (int i = 0; i < rx.length; i++) {
                double cx = pad + (rx[i] - xMin) / xRange * w;
                double cy = pad + h - (ry[i] - yMin) / yRange * h;
                Ellipse2D dot = new Ellipse2D.Double(
                        cx - dotR, cy - dotR, 2 * dotR, 2 * dotR);
                g2.fill(dot);
            }
        }

        // Legend
        int ly = pad + 15;
        String[] names = new String[results.size() + 1];
        for (int m = 0; m < results.size(); m++) {
            names[m] = results.get(m).getMethodName();
        }
        names[results.size()] = "Exact solution";
        for (int i = 0; i < names.length; i++) {
            g2.setColor(i < results.size() ? COLORS[i % 3] : COLORS[3]);
            g2.setStroke(i < results.size() ? SOLID : DASHED);
            int lx = pad + w - 160;
            g2.drawLine(lx, ly, lx + 20, ly);
            g2.setColor(Color.BLACK);
            g2.drawString(names[i], lx + 25, ly + 4);
            ly += 18;
        }
    }
}
