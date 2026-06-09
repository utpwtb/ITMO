package com.itmo.gui;

import com.itmo.methods.ImprovedEulerMethod;
import com.itmo.methods.MilneMethod;
import com.itmo.methods.RungeKuttaMethod;
import com.itmo.model.SolveResult;
import com.itmo.ode.ODE;

import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Main application window.
 * Layout: top = input, bottom = (left: results table, right: plot).
 */
public class MainFrame extends JFrame {

    private final InputPanel inputPanel;
    private final ResultTablePanel resultTablePanel;
    private PlotPanel plotPanel;
    private final JSplitPane bottomSplit;

    public MainFrame() {
        setTitle("Lab 6 — Numerical Solution of ODEs (Variant 14)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Top: input
        inputPanel = new InputPanel();
        add(inputPanel, BorderLayout.NORTH);

        // Bottom: left (table) + right (plot)
        resultTablePanel = new ResultTablePanel();
        plotPanel = new PlotPanel();
        bottomSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT,
                resultTablePanel, plotPanel);
        bottomSplit.setResizeWeight(0.55);
        add(bottomSplit, BorderLayout.CENTER);

        // Compute action
        inputPanel.onCompute(e -> compute());

        setSize(1100, 750);
        setLocationRelativeTo(null);
    }

    private void compute() {
        try {
            ODE ode = inputPanel.getSelectedODE();
            double x0 = inputPanel.getX0();
            double y0 = inputPanel.getY0();
            double xn = inputPanel.getXn();
            double h  = inputPanel.getH();
            double eps = inputPanel.getEps();

            if (xn <= x0) {
                JOptionPane.showMessageDialog(this,
                        "xn must be greater than x0", "Input Error",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }
            if (h <= 0) {
                JOptionPane.showMessageDialog(this,
                        "h must be positive", "Input Error",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }

            List<SolveResult> results = new ArrayList<>();
            List<String> methodNames = new ArrayList<>();

            if (inputPanel.useEuler()) {
                SolveResult r = new ImprovedEulerMethod().solve(ode, x0, y0, xn, h);
                results.add(r);
                methodNames.add(r.getMethodName());
            }
            if (inputPanel.useRK4()) {
                SolveResult r = new RungeKuttaMethod().solve(ode, x0, y0, xn, h);
                results.add(r);
                methodNames.add(r.getMethodName());
            }
            if (inputPanel.useMilne()) {
                SolveResult r = MilneMethod.solve(ode, x0, y0, xn, h);
                results.add(r);
                methodNames.add(r.getMethodName());
            }

            if (results.isEmpty()) {
                JOptionPane.showMessageDialog(this,
                        "Select at least one method", "Input Error",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }

            // Build exact solution
            int n = (int) Math.round((xn - x0) / h);
            double[] exactX = new double[n + 1];
            double[] exactY = new double[n + 1];
            for (int i = 0; i <= n; i++) {
                exactX[i] = x0 + i * h;
                exactY[i] = ode.exact(exactX[i], x0, y0);
            }

            // Display table
            double[][] allY = new double[results.size()][];
            String[] namesArr = methodNames.toArray(new String[0]);
            double[] errors = new double[results.size()];
            String[] errorTypes = new String[results.size()];

            for (int i = 0; i < results.size(); i++) {
                allY[i] = results.get(i).getY();
                errors[i] = results.get(i).getError();
                errorTypes[i] = results.get(i).getErrorMethod();
            }

            resultTablePanel.displayResults(namesArr, allY, exactX, exactY);
            resultTablePanel.displayErrors(namesArr, errors, errorTypes);

            // Update plot
            plotPanel = new PlotPanel(results, exactX, exactY);
            bottomSplit.setRightComponent(plotPanel);
            bottomSplit.revalidate();

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this,
                    "Invalid numeric input: " + ex.getMessage(),
                    "Input Error", JOptionPane.ERROR_MESSAGE);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this,
                    "Error: " + ex.getMessage(),
                    "Computation Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
