package org.example;

import org.example.engine.LSMSolver;
import org.example.model.ApproximationResult;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.awt.image.BufferedImage;
import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class BatchRunner {

    private static final Color[] COLORS = {
            Color.RED, Color.BLUE, new Color(0, 150, 0),
            Color.MAGENTA, new Color(139, 69, 19), Color.ORANGE
    };
    private static final String[] NAMES = {"线性函数", "二次多项式", "三次多项式", "指数函数", "对数函数", "幂函数"};
    private static final int PADDING = 60;

    public static void main(String[] args) throws Exception {
        String outDir = args.length > 0 ? args[0] : "C:\\develop\\NOTE_UTP\\StudyNote\\4 Вычислительная Математика\\Лаб\\Lab4\\Отчёт\\pic";

        // Test 1: Option 14 data
        List<Double> x1 = new ArrayList<>();
        List<Double> y1 = new ArrayList<>();
        for (int i = 0; i <= 10; i++) {
            double xi = i * 0.4;
            double yi = 25.0 * xi / (xi * xi * xi * xi + 14.0);
            x1.add(xi);
            y1.add(yi);
        }
        runTest("测试1 - 选项14", x1, y1, outDir, "test1");

        // Test 2: Random-like data
        List<Double> x2 = Arrays.asList(1.1, 2.3, 3.7, 4.5, 5.4, 6.8, 7.5);
        List<Double> y2 = Arrays.asList(2.73, 5.12, 7.74, 8.91, 10.59, 12.75, 13.43);
        runTest("测试2 - 讲座示例数据", x2, y2, outDir, "test2");

        // Test 3: Another random dataset
        List<Double> x3 = Arrays.asList(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0);
        List<Double> y3 = Arrays.asList(2.1, 4.0, 5.8, 8.2, 10.1, 12.3, 14.5, 16.7, 18.9, 21.0);
        runTest("测试3 - 随机数据", x3, y3, outDir, "test3");
    }

    private static void runTest(String title, List<Double> x, List<Double> y, String outDir, String prefix) throws Exception {
        System.out.println("Running: " + title);

        List<ApproximationResult> results = LSMSolver.computeAll(x, y);

        // Save text results
        StringBuilder sb = new StringBuilder();
        sb.append("==================== ").append(title).append(" ====================\n\n");
        sb.append(String.format("数据点数: %d\n\n", x.size()));

        ApproximationResult best = null;
        double minDelta = Double.MAX_VALUE;

        for (ApproximationResult r : results) {
            if (r.getDelta() < minDelta) {
                minDelta = r.getDelta();
                best = r;
            }

            sb.append("--------------------------------------------------------------\n");
            sb.append(String.format("【%s】\n", r.getFunctionType()));
            sb.append(String.format("  逼近公式: %s\n", r.getFormula()));
            sb.append(String.format("  偏差度量 S = %.6f\n", r.getS()));
            sb.append(String.format("  均方根偏差 = %.6f\n", r.getDelta()));
            sb.append(String.format("  决定系数 R^2 = %.6f\n", r.getR2()));
            sb.append(String.format("  评价: %s\n", r.getR2Message()));

            if (r.getFunctionType().equals("线性函数")) {
                sb.append(String.format("  皮尔逊相关系数 r = %.6f\n", r.getPearsonR()));
            }

            sb.append("\n  数据点详情:\n");
            sb.append(String.format("  %6s %12s %12s %12s %12s\n", "x", "y", "phi(x)", "epsilon", "|eps|"));
            sb.append("  ---------------------------------------------------------\n");
            double[] yPred = r.getYPredicted();
            double[] res = r.getResiduals();
            if (yPred != null && res != null) {
                for (int i = 0; i < x.size(); i++) {
                    sb.append(String.format("  %6.2f %12.4f %12.4f %12.4f %12.4f\n",
                            x.get(i), y.get(i), yPred[i], res[i], Math.abs(res[i])));
                }
            }
            sb.append("\n");
        }

        sb.append("==============================================================\n");
        if (best != null) {
            sb.append(String.format("\n最佳逼近: 【%s】\n", best.getFunctionType()));
            sb.append(String.format("  公式: %s\n", best.getFormula()));
            sb.append(String.format("  均方根偏差: %.6f\n", best.getDelta()));
        }

        try (PrintWriter pw = new PrintWriter(
                new OutputStreamWriter(new FileOutputStream(outDir + "/" + prefix + "_result.txt"), "UTF-8"))) {
            pw.print(sb.toString());
        }
        System.out.println(sb.toString());

        // Generate chart
        BufferedImage img = drawChart(x, y, results);
        ImageIO.write(img, "png", new File(outDir + "/" + prefix + "_chart.png"));
        System.out.println("Chart saved: " + prefix + "_chart.png\n");
    }

    private static BufferedImage drawChart(List<Double> x, List<Double> y, List<ApproximationResult> results) {
        int w = 800, h = 600;
        BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2 = img.createGraphics();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setColor(Color.WHITE);
        g2.fillRect(0, 0, w, h);

        double minX = x.stream().mapToDouble(Double::doubleValue).min().orElse(0);
        double maxX = x.stream().mapToDouble(Double::doubleValue).max().orElse(1);
        double minY = y.stream().mapToDouble(Double::doubleValue).min().orElse(0);
        double maxY = y.stream().mapToDouble(Double::doubleValue).max().orElse(1);

        for (ApproximationResult r : results) {
            if (r.getDelta() >= Double.MAX_VALUE) continue;
            double[] yp = r.getYPredicted();
            if (yp != null) {
                for (double v : yp) {
                    minY = Math.min(minY, v);
                    maxY = Math.max(maxY, v);
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
        double scaleX = (w - 2 * PADDING) / xSpan;
        double scaleY = (h - 2 * PADDING) / ySpan;
        final double _minX = minX, _minY = minY;

        // Grid
        g2.setColor(new Color(220, 220, 220));
        g2.setStroke(new BasicStroke(1));
        int gridLines = 10;
        for (int i = 0; i <= gridLines; i++) {
            int gx = PADDING + i * (w - 2 * PADDING) / gridLines;
            int gy = PADDING + i * (h - 2 * PADDING) / gridLines;
            g2.drawLine(gx, PADDING, gx, h - PADDING);
            g2.drawLine(PADDING, gy, w - PADDING, gy);
        }

        // Axes
        g2.setColor(Color.BLACK);
        g2.setStroke(new BasicStroke(2));
        g2.drawLine(PADDING, h - PADDING, w - PADDING, h - PADDING);
        g2.drawLine(PADDING, PADDING, PADDING, h - PADDING);

        // Labels
        g2.setFont(new Font("Consolas", Font.PLAIN, 10));
        for (int i = 0; i <= gridLines; i++) {
            double xVal = minX + i * xSpan / gridLines;
            double yVal = maxY - i * ySpan / gridLines;
            int tx = (int) (PADDING + (xVal - _minX) * scaleX);
            int ty = (int) (h - PADDING - (yVal - _minY) * scaleY);
            g2.drawString(String.format("%.2f", xVal), tx - 15, h - PADDING + 18);
            g2.drawString(String.format("%.2f", yVal), PADDING - 55, ty + 5);
        }

        // Fit curves
        for (int idx = 0; idx < results.size(); idx++) {
            ApproximationResult r = results.get(idx);
            if (r.getDelta() >= Double.MAX_VALUE) continue;

            g2.setColor(COLORS[idx % COLORS.length]);
            g2.setStroke(new BasicStroke(2));

            Path2D.Double path = new Path2D.Double();
            int numPts = 500;
            for (int i = 0; i <= numPts; i++) {
                double xp = minX + i * xSpan / numPts;
                double yp = 0;
                double[] c = r.getCoefficients();
                switch (r.getFunctionType()) {
                    case "线性函数": yp = c[0] * xp + c[1]; break;
                    case "二次多项式": yp = c[0] + c[1] * xp + c[2] * xp * xp; break;
                    case "三次多项式": yp = c[0] + c[1] * xp + c[2] * xp * xp + c[3] * xp * xp * xp; break;
                    case "指数函数": yp = c[0] * Math.exp(c[1] * xp); break;
                    case "对数函数": yp = xp > 0 ? c[0] * Math.log(xp) + c[1] : c[1]; break;
                    case "幂函数": yp = xp > 0 ? c[0] * Math.pow(xp, c[1]) : 0; break;
                }
                int px = (int) (PADDING + (xp - _minX) * scaleX);
                int py = (int) (h - PADDING - (yp - _minY) * scaleY);
                if (i == 0) path.moveTo(px, py);
                else path.lineTo(px, py);
            }
            g2.draw(path);
        }

        // Data points
        g2.setColor(Color.BLACK);
        for (int i = 0; i < x.size(); i++) {
            int px = (int) (PADDING + (x.get(i) - _minX) * scaleX);
            int py = (int) (h - PADDING - (y.get(i) - _minY) * scaleY);
            Ellipse2D.Double dot = new Ellipse2D.Double(px - 4, py - 4, 8, 8);
            g2.fill(dot);
        }

        // Legend
        int legendX = w - 220, legendY = PADDING + 5;
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

        g2.dispose();
        return img;
    }
}
