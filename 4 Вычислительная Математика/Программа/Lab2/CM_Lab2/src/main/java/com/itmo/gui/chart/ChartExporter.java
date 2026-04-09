package com.itmo.gui.chart;

import com.itmo.core.functions.EquationInfo;
import com.itmo.core.functions.SystemInfo;
import com.itmo.core.functions.SystemFunction2D;
import io.fair_acc.chartfx.XYChart;
import io.fair_acc.chartfx.axes.spi.DefaultNumericAxis;
import io.fair_acc.chartfx.plugins.Zoomer;
import io.fair_acc.dataset.spi.DoubleDataSet;

import java.util.ArrayList;
import java.util.List;

public final class ChartExporter {
    private static final double GRAD_H = 1e-7;
    private static final int MAX_TRACE_STEPS = 5000;
    private static final int NEWTON_ITER = 10;
    private static final int EXPLICIT_SAMPLES = 600;

    private ChartExporter() {}

    public static XYChart createEquationChart(EquationInfo equation, double a, double b) {
        DefaultNumericAxis xAxis = new DefaultNumericAxis("x");
        DefaultNumericAxis yAxis = new DefaultNumericAxis("y");
        xAxis.setAutoRangeRounding(false);
        yAxis.setAutoRangeRounding(false);

        XYChart chart = new XYChart(xAxis, yAxis);
        chart.setTitle("f(x) = " + equation.getEquationString().replace(" = 0", ""));
        chart.setLegendVisible(true);

        DoubleDataSet dataSet = new DoubleDataSet("f(x)");
        dataSet.setStyle("stroke-width: 2; marker-type: none;");
        int numPoints = 500;
        double yMinData = Double.MAX_VALUE;
        double yMaxData = Double.MIN_VALUE;
        for (int i = 0; i <= numPoints; i++) {
            double x = a + (b - a) * i / numPoints;
            double y = equation.getFunction().evaluate(x);
            if (!Double.isNaN(y) && !Double.isInfinite(y) && y > -1000 && y < 1000) {
                dataSet.add(x, y);
                yMinData = Math.min(yMinData, y);
                yMaxData = Math.max(yMaxData, y);
            }
        }

        chart.getDatasets().add(dataSet);
        enableZoom(chart, a, b,
                yMinData == Double.MAX_VALUE ? -10 : yMinData - (yMaxData - yMinData) * 0.05,
                yMaxData == Double.MIN_VALUE ? 10 : yMaxData + (yMaxData - yMinData) * 0.05);
        return chart;
    }

    public static XYChart createSystemChart(SystemInfo system, double xSolution, double ySolution) {
        DefaultNumericAxis xAxis = new DefaultNumericAxis("x");
        DefaultNumericAxis yAxis = new DefaultNumericAxis("y");
        xAxis.setAutoRangeRounding(false);
        yAxis.setAutoRangeRounding(false);

        XYChart chart = new XYChart(xAxis, yAxis);
        chart.setTitle("Система нелинейных уравнений");
        chart.setLegendVisible(true);

        double range = 4.0;
        double xMin = Math.max(-10.0, xSolution - range);
        double xMax = Math.min(10.0, xSolution + range);
        double yMin = Math.max(-10.0, ySolution - range);
        double yMax = Math.min(10.0, ySolution + range);

        List<DoubleDataSet> curves1 = createImplicitCurveDatasets(system.getF1(), xMin, xMax, yMin, yMax, system.getEq1String());
        List<DoubleDataSet> curves2 = createImplicitCurveDatasets(system.getF2(), xMin, xMax, yMin, yMax, system.getEq2String());

        for (DoubleDataSet ds : curves1) {
            chart.getDatasets().add(ds);
        }
        for (DoubleDataSet ds : curves2) {
            chart.getDatasets().add(ds);
        }

        enableZoom(chart, xMin, xMax, yMin, yMax);
        return chart;
    }

    private static List<DoubleDataSet> createImplicitCurveDatasets(SystemFunction2D func,
                                                                    double xMin, double xMax,
                                                                    double yMin, double yMax,
                                                                    String baseName) {

        boolean explicitY = isExplicitYFunction(func, xMin, xMax, yMin, yMax);
        if (explicitY) {
            return createExplicitYDataset(func, xMin, xMax, yMin, yMax, baseName);
        }

        return createContourTracedCurves(func, xMin, xMax, yMin, yMax, baseName);
    }

    private static boolean isExplicitYFunction(SystemFunction2D func,
                                                double xMin, double xMax,
                                                double yMin, double yMax) {
        int testPoints = 30;
        double dx = (xMax - xMin) / testPoints;
        double dy = (yMax - yMin) / testPoints;
        double minDfdyAbs = Double.MAX_VALUE;

        for (int i = 0; i <= testPoints; i++) {
            for (int j = 0; j <= testPoints; j++) {
                double x = xMin + i * dx;
                double y = yMin + j * dy;
                double dfdy = (func.evaluate(x, y + GRAD_H) - func.evaluate(x, y - GRAD_H)) / (2 * GRAD_H);
                if (!Double.isNaN(dfdy)) {
                    minDfdyAbs = Math.min(minDfdyAbs, Math.abs(dfdy));
                }
            }
        }

        return minDfdyAbs > 0.3;
    }

    private static List<DoubleDataSet> createExplicitYDataset(SystemFunction2D func,
                                                               double xMin, double xMax,
                                                               double yMin, double yMax,
                                                               String baseName) {
        List<DoubleDataSet> result = new ArrayList<>();
        DoubleDataSet ds = new DoubleDataSet(baseName);
        ds.setStyle("stroke-width: 2; marker-type: none;");
        double dx = (xMax - xMin) / EXPLICIT_SAMPLES;

        for (int i = 0; i <= EXPLICIT_SAMPLES; i++) {
            double x = xMin + i * dx;
            double yLo = yMin;
            double yHi = yMax;
            double fLo = func.evaluate(x, yLo);
            double fHi = func.evaluate(x, yHi);

            if (Double.isNaN(fLo) || Double.isNaN(fHi)) continue;
            if (Math.abs(fLo) < 1e-12) { ds.add(x, yLo); continue; }
            if (Math.abs(fHi) < 1e-12) { ds.add(x, yHi); continue; }

            if (fLo * fHi < 0) {
                double root = bisectY(func, x, yLo, yHi, fLo, fHi);
                if (!Double.isNaN(root)) {
                    ds.add(x, root);
                    continue;
                }
            }

            double[] guess = newtonGuessY(func, x, yMin, yMax);
            if (guess != null && guess[1] >= yMin - 0.5 && guess[1] <= yMax + 0.5) {
                ds.add(x, guess[1]);
            }
        }

        if (ds.getDataCount() > 1) {
            result.add(ds);
        }

        return result;
    }

    private static double[] newtonGuessY(SystemFunction2D func, double x, double yMin, double yMax) {
        double yMid = (yMin + yMax) / 2;
        double y = yMid;

        for (int iter = 0; iter < NEWTON_ITER; iter++) {
            double f = func.evaluate(x, y);
            if (Double.isNaN(f)) return null;
            if (Math.abs(f) < 1e-13) return new double[]{x, y};

            double dfdy = (func.evaluate(x, y + GRAD_H) - func.evaluate(x, y - GRAD_H)) / (2 * GRAD_H);
            if (Math.abs(dfdy) < 1e-15) return null;

            y -= f / dfdy;
            if (Double.isNaN(y) || Double.isInfinite(y)) return null;
        }

        double fFinal = func.evaluate(x, y);
        if (Double.isNaN(fFinal) || Math.abs(fFinal) > 1e-6) return null;

        return new double[]{x, y};
    }

    private static List<DoubleDataSet> createContourTracedCurves(SystemFunction2D func,
                                                                  double xMin, double xMax,
                                                                  double yMin, double yMax,
                                                                  String baseName) {
        double stepSize = Math.min(xMax - xMin, yMax - yMin) / 500;
        int gridRes = 400;
        double gxStep = (xMax - xMin) / gridRes;
        double gyStep = (yMax - yMin) / gridRes;
        boolean[][] visited = new boolean[gridRes + 1][gridRes + 1];

        List<double[]> seeds = new ArrayList<>();

        addVerticalSeeds(func, xMin, yMin, yMax, seeds);
        addHorizontalSeeds(func, yMin, xMin, xMax, seeds);

        for (int k = 1; k <= 7; k++) {
            double x = xMin + (xMax - xMin) * k / 8;
            addVerticalSeeds(func, x, yMin, yMax, seeds);
        }
        for (int k = 1; k <= 7; k++) {
            double y = yMin + (yMax - yMin) * k / 8;
            addHorizontalSeeds(func, y, xMin, xMax, seeds);
        }

        List<List<double[]>> curves = new ArrayList<>();

        for (double[] seed : seeds) {
            if (isNearVisited(seed, xMin, yMin, gxStep, gyStep, gridRes, visited)) continue;

            List<double[]> forward = traceCurve(func, seed[0], seed[1], +1, stepSize, xMin, xMax, yMin, yMax);
            List<double[]> backward = traceCurve(func, seed[0], seed[1], -1, stepSize, xMin, xMax, yMin, yMax);

            List<double[]> curve = new ArrayList<>();
            for (int i = backward.size() - 1; i >= 1; i--) {
                curve.add(backward.get(i));
            }
            curve.addAll(forward);

            if (curve.size() < 2) continue;

            markVisited(curve, xMin, yMin, gxStep, gyStep, gridRes, visited);
            curves.add(curve);
        }

        List<DoubleDataSet> result = new ArrayList<>();
        for (int i = 0; i < curves.size(); i++) {
            List<double[]> curve = curves.get(i);
            String name = curves.size() == 1 ? baseName : baseName + " (" + (i + 1) + ")";
            DoubleDataSet ds = new DoubleDataSet(name);
            ds.setStyle("stroke-width: 2; marker-type: none;");
            for (double[] pt : curve) {
                ds.add(pt[0], pt[1]);
            }
            result.add(ds);
        }

        return result;
    }

    private static void addVerticalSeeds(SystemFunction2D func, double x, double yMin, double yMax, List<double[]> seeds) {
        int numYSteps = 3000;
        double yStep = (yMax - yMin) / numYSteps;
        double prevY = yMin;
        double prevF = func.evaluate(x, prevY);

        for (int j = 1; j <= numYSteps; j++) {
            double y = yMin + j * yStep;
            double f = func.evaluate(x, y);

            if (!Double.isNaN(prevF) && !Double.isNaN(f) && prevF * f < 0) {
                double root = bisectY(func, x, prevY, y, prevF, f);
                if (!Double.isNaN(root)) {
                    seeds.add(new double[]{x, root});
                }
            }

            prevY = y;
            prevF = f;
        }
    }

    private static void addHorizontalSeeds(SystemFunction2D func, double y, double xMin, double xMax, List<double[]> seeds) {
        int numXSteps = 3000;
        double xStep = (xMax - xMin) / numXSteps;
        double prevX = xMin;
        double prevF = func.evaluate(prevX, y);

        for (int i = 1; i <= numXSteps; i++) {
            double x = xMin + i * xStep;
            double f = func.evaluate(x, y);

            if (!Double.isNaN(prevF) && !Double.isNaN(f) && prevF * f < 0) {
                double root = bisectX(func, prevX, x, y, prevF, f);
                if (!Double.isNaN(root)) {
                    seeds.add(new double[]{root, y});
                }
            }

            prevX = x;
            prevF = f;
        }
    }

    private static boolean isNearVisited(double[] pt, double xMin, double yMin,
                                          double gxStep, double gyStep, int gridRes,
                                          boolean[][] visited) {
        int gi = clamp((int) ((pt[0] - xMin) / gxStep), 0, gridRes);
        int gj = clamp((int) ((pt[1] - yMin) / gyStep), 0, gridRes);
        for (int di = -3; di <= 3; di++) {
            for (int dj = -3; dj <= 3; dj++) {
                int ni = gi + di;
                int nj = gj + dj;
                if (ni >= 0 && ni <= gridRes && nj >= 0 && nj <= gridRes && visited[ni][nj]) {
                    return true;
                }
            }
        }
        return false;
    }

    private static void markVisited(List<double[]> curve, double xMin, double yMin,
                                     double gxStep, double gyStep, int gridRes,
                                     boolean[][] visited) {
        for (double[] pt : curve) {
            int ci = clamp((int) ((pt[0] - xMin) / gxStep), 0, gridRes);
            int cj = clamp((int) ((pt[1] - yMin) / gyStep), 0, gridRes);
            for (int di = -2; di <= 2; di++) {
                for (int dj = -2; dj <= 2; dj++) {
                    int ni = ci + di;
                    int nj = cj + dj;
                    if (ni >= 0 && ni <= gridRes && nj >= 0 && nj <= gridRes) {
                        visited[ni][nj] = true;
                    }
                }
            }
        }
    }

    private static List<double[]> traceCurve(SystemFunction2D func, double x0, double y0, int direction,
                                              double stepSize, double xMin, double xMax, double yMin, double yMax) {
        List<double[]> curve = new ArrayList<>();
        curve.add(new double[]{x0, y0});

        double startX = x0;
        double startY = y0;

        for (int i = 0; i < MAX_TRACE_STEPS; i++) {
            double[] grad = gradient(func, x0, y0);
            double dfdx = grad[0];
            double dfdy = grad[1];

            double gradSq = dfdx * dfdx + dfdy * dfdy;
            if (gradSq < 1e-20) break;

            double tx = -dfdy * direction;
            double ty = dfdx * direction;

            double length = Math.sqrt(tx * tx + ty * ty);
            tx /= length;
            ty /= length;

            double[] next = new double[]{x0 + stepSize * tx, y0 + stepSize * ty};

            if (next[0] < xMin || next[0] > xMax || next[1] < yMin || next[1] > yMax) break;

            boolean converged = newtonCorrect(func, next);
            if (!converged) break;

            double x1 = next[0];
            double y1 = next[1];

            if (x1 < xMin || x1 > xMax || y1 < yMin || y1 > yMax) break;

            double dx = x1 - startX;
            double dy = y1 - startY;
            if (i > 20 && dx * dx + dy * dy < stepSize * stepSize * 4) break;

            curve.add(new double[]{x1, y1});
            x0 = x1;
            y0 = y1;
        }

        return curve;
    }

    private static boolean newtonCorrect(SystemFunction2D func, double[] xy) {
        double x = xy[0];
        double y = xy[1];

        for (int i = 0; i < NEWTON_ITER; i++) {
            double f = func.evaluate(x, y);
            if (Double.isNaN(f)) return false;
            if (Math.abs(f) < 1e-13) {
                xy[0] = x;
                xy[1] = y;
                return true;
            }

            double[] grad = gradient(func, x, y);
            double gradSq = grad[0] * grad[0] + grad[1] * grad[1];
            if (gradSq < 1e-20) return false;

            x -= f * grad[0] / gradSq;
            y -= f * grad[1] / gradSq;

            if (Double.isNaN(x) || Double.isNaN(y) || Double.isInfinite(x) || Double.isInfinite(y)) {
                return false;
            }
        }

        double fFinal = func.evaluate(x, y);
        if (Double.isNaN(fFinal) || Math.abs(fFinal) > 1e-6) return false;

        xy[0] = x;
        xy[1] = y;
        return true;
    }

    private static double[] gradient(SystemFunction2D func, double x, double y) {
        double dfdx = (func.evaluate(x + GRAD_H, y) - func.evaluate(x - GRAD_H, y)) / (2 * GRAD_H);
        double dfdy = (func.evaluate(x, y + GRAD_H) - func.evaluate(x, y - GRAD_H)) / (2 * GRAD_H);
        return new double[]{dfdx, dfdy};
    }

    private static double bisectY(SystemFunction2D func, double x, double yLo, double yHi, double fLo, double fHi) {
        for (int i = 0; i < 60; i++) {
            double yMid = (yLo + yHi) / 2;
            double fMid = func.evaluate(x, yMid);
            if (Double.isNaN(fMid)) return Double.NaN;
            if (Math.abs(fMid) < 1e-14) return yMid;
            if (fLo * fMid < 0) {
                yHi = yMid;
                fHi = fMid;
            } else {
                yLo = yMid;
                fLo = fMid;
            }
        }
        return (yLo + yHi) / 2;
    }

    private static double bisectX(SystemFunction2D func, double xLo, double xHi, double y, double fLo, double fHi) {
        for (int i = 0; i < 60; i++) {
            double xMid = (xLo + xHi) / 2;
            double fMid = func.evaluate(xMid, y);
            if (Double.isNaN(fMid)) return Double.NaN;
            if (Math.abs(fMid) < 1e-14) return xMid;
            if (fLo * fMid < 0) {
                xHi = xMid;
                fHi = fMid;
            } else {
                xLo = xMid;
                fLo = fMid;
            }
        }
        return (xLo + xHi) / 2;
    }

    private static int clamp(int val, int min, int max) {
        return Math.max(min, Math.min(max, val));
    }

    private static void enableZoom(XYChart chart, double xMin, double xMax, double yMin, double yMax) {
        DefaultNumericAxis xAxis = (DefaultNumericAxis) chart.getXAxis();
        DefaultNumericAxis yAxis = (DefaultNumericAxis) chart.getYAxis();

        double xPad = (xMax - xMin) * 0.02;
        double yPad = (yMax - yMin) * 0.02;

        double xLo = xMin - xPad;
        double xHi = xMax + xPad;
        double yLo = yMin - yPad;
        double yHi = yMax + yPad;

        xAxis.setAutoRanging(false);
        yAxis.setAutoRanging(false);
        xAxis.setMin(xLo);
        xAxis.setMax(xHi);
        yAxis.setMin(yLo);
        yAxis.setMax(yHi);

        double minXRange = (xMax - xMin) * 0.01;
        double minYRange = (yMax - yMin) * 0.01;
        xAxis.minProperty().addListener((obs, old, val) -> {
            double v = val.doubleValue();
            if (xAxis.getMax() - v < minXRange) { xAxis.setMin(xAxis.getMax() - minXRange); }
            if (v < xLo) { xAxis.setMin(xLo); }
        });
        xAxis.maxProperty().addListener((obs, old, val) -> {
            double v = val.doubleValue();
            if (v - xAxis.getMin() < minXRange) { xAxis.setMax(xAxis.getMin() + minXRange); }
            if (v > xHi) { xAxis.setMax(xHi); }
        });
        yAxis.minProperty().addListener((obs, old, val) -> {
            double v = val.doubleValue();
            if (yAxis.getMax() - v < minYRange) { yAxis.setMin(yAxis.getMax() - minYRange); }
            if (v < yLo) { yAxis.setMin(yLo); }
        });
        yAxis.maxProperty().addListener((obs, old, val) -> {
            double v = val.doubleValue();
            if (v - yAxis.getMin() < minYRange) { yAxis.setMax(yAxis.getMin() + minYRange); }
            if (v > yHi) { yAxis.setMax(yHi); }
        });

        Zoomer zoomer = new Zoomer();
        zoomer.setAutoZoomEnabled(true);
        chart.getPlugins().add(zoomer);
    }
}
