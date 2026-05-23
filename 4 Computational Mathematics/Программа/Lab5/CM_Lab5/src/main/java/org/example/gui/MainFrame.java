package org.example.gui;

import org.example.engine.*;
import org.example.model.InputData;
import org.example.model.InterpolationResult;
import org.example.service.DataLoader;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class MainFrame extends JFrame {

    // Data
    private InputData currentData;
    private final List<InterpolationResult> results = new ArrayList<>();

    // Input components
    private JTextField xField, yField, x1Field, x2Field;
    private JTextField filePathField;
    private JTextField funcAField, funcBField, funcNField;
    private JComboBox<String> funcCombo;
    private JTabbedPane inputTabs;

    // Result components
    private JTable diffTable;
    private DefaultTableModel diffTableModel;
    private JTextArea resultArea;

    // Chart
    private ChartPanel chartPanel;

    // Method checkboxes
    private JCheckBox cbLagrange, cbNewton, cbGauss, cbStirling, cbBessel;

    public MainFrame() {
        setTitle("Lab5 - Function Interpolation (Variant 14)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1250, 750);
        setLocationRelativeTo(null);
        initUI();
    }

    private void initUI() {
        setLayout(new BorderLayout(8, 8));

        // === TOP: Input Panel ===
        JPanel topPanel = new JPanel(new BorderLayout());
        inputTabs = new JTabbedPane();
        inputTabs.addTab("Manual", createManualPanel());
        inputTabs.addTab("File", createFilePanel());
        inputTabs.addTab("Function", createFunctionPanel());
        topPanel.add(inputTabs, BorderLayout.CENTER);

        // Method selection
        JPanel methodPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 4));
        methodPanel.setBorder(BorderFactory.createTitledBorder("Methods"));
        cbLagrange = new JCheckBox("Lagrange", true);
        cbNewton = new JCheckBox("Newton", true);
        cbGauss = new JCheckBox("Gauss", true);
        cbStirling = new JCheckBox("Stirling (extra)", true);
        cbBessel = new JCheckBox("Bessel (extra)", true);
        methodPanel.add(cbLagrange);
        methodPanel.add(cbNewton);
        methodPanel.add(cbGauss);
        methodPanel.add(cbStirling);
        methodPanel.add(cbBessel);

        // Target X fields
        methodPanel.add(new JLabel("  X1:"));
        x1Field = new JTextField("1.112", 6);
        methodPanel.add(x1Field);
        methodPanel.add(new JLabel("X2:"));
        x2Field = new JTextField("1.319", 6);
        methodPanel.add(x2Field);

        JButton computeBtn = new JButton("Compute");
        computeBtn.setFont(new Font("SansSerif", Font.BOLD, 13));
        computeBtn.addActionListener(e -> compute());
        methodPanel.add(computeBtn);

        JButton loadDemoBtn = new JButton("Load Variant 14");
        loadDemoBtn.addActionListener(e -> loadVariant14());
        methodPanel.add(loadDemoBtn);

        topPanel.add(methodPanel, BorderLayout.SOUTH);
        add(topPanel, BorderLayout.NORTH);

        // === CENTER: Results + Chart ===
        JSplitPane centerSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        centerSplit.setResizeWeight(0.55);

        // Left: tables
        JPanel leftPanel = new JPanel(new BorderLayout(5, 5));

        // Finite difference table
        diffTableModel = new DefaultTableModel();
        diffTable = new JTable(diffTableModel);
        diffTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        JScrollPane diffScroll = new JScrollPane(diffTable);
        diffScroll.setBorder(BorderFactory.createTitledBorder(
                "Finite Difference Table"));
        diffScroll.setPreferredSize(new Dimension(550, 220));
        leftPanel.add(diffScroll, BorderLayout.NORTH);

        // Interpolation results
        resultArea = new JTextArea();
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        JScrollPane resultScroll = new JScrollPane(resultArea);
        resultScroll.setBorder(BorderFactory.createTitledBorder(
                "Interpolation Results"));
        leftPanel.add(resultScroll, BorderLayout.CENTER);

        centerSplit.setLeftComponent(leftPanel);

        // Right: Chart
        chartPanel = new ChartPanel();
        chartPanel.setBorder(BorderFactory.createTitledBorder("Graph"));
        centerSplit.setRightComponent(chartPanel);

        add(centerSplit, BorderLayout.CENTER);
    }

    private JPanel createManualPanel() {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3, 4, 3, 4);
        c.fill = GridBagConstraints.HORIZONTAL;

        c.gridx = 0; c.gridy = 0;
        p.add(new JLabel("X values (comma-separated):"), c);
        c.gridx = 1; c.weightx = 1.0;
        xField = new JTextField(
                "1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65", 40);
        p.add(xField, c);

        c.gridx = 0; c.gridy = 1; c.weightx = 0;
        p.add(new JLabel("Y values (comma-separated):"), c);
        c.gridx = 1; c.weightx = 1.0;
        yField = new JTextField(
                "0.1213, 1.1316, 2.1459, 3.1565, 4.1571, 5.1819, 6.1969", 40);
        p.add(yField, c);

        return p;
    }

    private JPanel createFilePanel() {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3, 4, 3, 4);
        c.fill = GridBagConstraints.HORIZONTAL;

        c.gridx = 0;
        p.add(new JLabel("File path:"), c);
        c.gridx = 1; c.weightx = 1.0;
        filePathField = new JTextField("test_data/variant14.txt", 30);
        p.add(filePathField, c);
        c.gridx = 2; c.weightx = 0;
        JButton browseBtn = new JButton("Browse...");
        browseBtn.addActionListener(e -> {
            JFileChooser fc = new JFileChooser(".");
            if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
                filePathField.setText(fc.getSelectedFile().getPath());
            }
        });
        p.add(browseBtn, c);

        return p;
    }

    private JPanel createFunctionPanel() {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3, 4, 3, 4);
        c.fill = GridBagConstraints.HORIZONTAL;

        c.gridx = 0; c.gridy = 0;
        p.add(new JLabel("Function:"), c);
        funcCombo = new JComboBox<>(new String[]{
                "sin(x)", "cos(x)", "exp(x)", "x^2", "ln(x)"
        });
        c.gridx = 1; c.gridwidth = 3;
        p.add(funcCombo, c);

        c.gridx = 0; c.gridy = 1; c.gridwidth = 1;
        p.add(new JLabel("From a:"), c);
        funcAField = new JTextField("0.0", 6);
        c.gridx = 1;
        p.add(funcAField, c);
        p.add(new JLabel("To b:"), c);
        funcBField = new JTextField("3.0", 6);
        c.gridx = 3;
        p.add(funcBField, c);
        p.add(new JLabel("Points n:"), c);
        funcNField = new JTextField("7", 6);
        c.gridx = 5;
        p.add(funcNField, c);

        return p;
    }

    private void loadVariant14() {
        xField.setText("1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65");
        yField.setText("0.1213, 1.1316, 2.1459, 3.1565, 4.1571, 5.1819, 6.1969");
        x1Field.setText("1.112");
        x2Field.setText("1.319");
        inputTabs.setSelectedIndex(0);
    }

    private void compute() {
        results.clear();
        resultArea.setText("");

        try {
            // Load data based on active tab
            int tab = inputTabs.getSelectedIndex();
            if (tab == 0) {
                currentData = loadFromManual();
            } else if (tab == 1) {
                currentData = loadFromFile();
            } else {
                currentData = loadFromFunction();
            }

            if (currentData == null || currentData.size() < 2) {
                JOptionPane.showMessageDialog(this,
                        "Need at least 2 data points.", "Error",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }

            double[] x = currentData.getX();
            double[] y = currentData.getY();

            // Check monotonic
            for (int i = 1; i < x.length; i++) {
                if (x[i] <= x[i - 1]) {
                    JOptionPane.showMessageDialog(this,
                            "X values must be strictly increasing.",
                            "Error", JOptionPane.ERROR_MESSAGE);
                    return;
                }
            }

            double x1 = Double.parseDouble(x1Field.getText().trim());
            double x2 = Double.parseDouble(x2Field.getText().trim());

            // Build finite difference table
            double[][] fd = FiniteDifferenceTable.build(y);
            updateDiffTable(x, fd);

            // Compute selected methods
            StringBuilder sb = new StringBuilder();
            sb.append("Source: ").append(currentData.getSourceDescription())
                    .append("\n\n");

            if (cbLagrange.isSelected()) {
                InterpolationResult r1 = LagrangeSolver.interpolate(x, y, x1);
                InterpolationResult r2 = LagrangeSolver.interpolate(x, y, x2);
                results.add(r1);
                results.add(r2);
                sb.append(formatResult(r1)).append("\n");
                sb.append(formatResult(r2)).append("\n\n");
            }

            if (cbNewton.isSelected()) {
                InterpolationResult r1 = NewtonSolver.interpolate(x, y, x1);
                InterpolationResult r2 = NewtonSolver.interpolate(x, y, x2);
                results.add(r1);
                results.add(r2);
                sb.append(formatResult(r1)).append("\n");
                sb.append(formatResult(r2)).append("\n\n");
            }

            if (cbGauss.isSelected()) {
                InterpolationResult r1 = GaussSolver.interpolate(x, y, x1);
                InterpolationResult r2 = GaussSolver.interpolate(x, y, x2);
                results.add(r1);
                results.add(r2);
                sb.append(formatResult(r1)).append("\n");
                sb.append(formatResult(r2)).append("\n\n");
            }

            if (cbStirling.isSelected()) {
                InterpolationResult r1 = StirlingSolver.interpolate(x, y, x1);
                InterpolationResult r2 = StirlingSolver.interpolate(x, y, x2);
                results.add(r1);
                results.add(r2);
                sb.append(formatResult(r1)).append("\n");
                sb.append(formatResult(r2)).append("\n\n");
            }

            if (cbBessel.isSelected()) {
                InterpolationResult r1 = BesselSolver.interpolate(x, y, x1);
                InterpolationResult r2 = BesselSolver.interpolate(x, y, x2);
                results.add(r1);
                results.add(r2);
                sb.append(formatResult(r1)).append("\n");
                sb.append(formatResult(r2)).append("\n\n");
            }

            resultArea.setText(sb.toString());
            chartPanel.setData(currentData, x1, x2, results);

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this,
                    "Invalid number format: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this,
                    "File error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private InputData loadFromManual() {
        String[] xs = xField.getText().trim().split("[,\\s]+");
        String[] ys = yField.getText().trim().split("[,\\s]+");
        if (xs.length != ys.length) {
            JOptionPane.showMessageDialog(this,
                    "X and Y must have the same number of values.",
                    "Error", JOptionPane.ERROR_MESSAGE);
            return null;
        }
        double[] x = new double[xs.length];
        double[] y = new double[ys.length];
        for (int i = 0; i < xs.length; i++) {
            x[i] = Double.parseDouble(xs[i].trim());
            y[i] = Double.parseDouble(ys[i].trim());
        }
        return DataLoader.fromArrays(x, y);
    }

    private InputData loadFromFile() throws IOException {
        String path = filePathField.getText().trim();
        if (path.isEmpty()) {
            JOptionPane.showMessageDialog(this,
                    "Please specify a file path.",
                    "Error", JOptionPane.ERROR_MESSAGE);
            return null;
        }
        return DataLoader.fromFile(path);
    }

    private InputData loadFromFunction() {
        double a = Double.parseDouble(funcAField.getText().trim());
        double b = Double.parseDouble(funcBField.getText().trim());
        int n = Integer.parseInt(funcNField.getText().trim());
        if (n < 2) {
            JOptionPane.showMessageDialog(this,
                    "Need at least 2 points (n >= 2).",
                    "Error", JOptionPane.ERROR_MESSAGE);
            return null;
        }
        String funcName = (String) funcCombo.getSelectedItem();
        Function<Double, Double> f = getFunction(funcName);
        return DataLoader.fromFunction(f, a, b, n);
    }

    private Function<Double, Double> getFunction(String name) {
        switch (name) {
            case "sin(x)": return Math::sin;
            case "cos(x)": return Math::cos;
            case "exp(x)": return Math::exp;
            case "x^2": return x -> x * x;
            case "ln(x)": return Math::log;
            default: return Math::sin;
        }
    }

    private void updateDiffTable(double[] x, double[][] fd) {
        int n = x.length;
        String[] cols = new String[n + 1];
        cols[0] = "x";
        cols[1] = "y";
        for (int j = 2; j <= n; j++) {
            cols[j] = "Δ" + (j - 1) + "y";
        }
        diffTableModel.setColumnIdentifiers(cols);

        Object[][] rows = new Object[n][n + 1];
        for (int i = 0; i < n; i++) {
            rows[i][0] = String.format("%.4f", x[i]);
            for (int j = 0; j < n - i; j++) {
                rows[i][j + 1] = String.format("%.6f", fd[i][j]);
            }
            for (int j = n - i; j < n; j++) {
                rows[i][j + 1] = "";
            }
        }

        // Replace the model data
        diffTableModel.setDataVector(rows,
                java.util.Arrays.asList(cols).toArray(new String[0]));

        // Auto-size columns
        for (int i = 0; i < diffTable.getColumnCount(); i++) {
            diffTable.getColumnModel().getColumn(i).setPreferredWidth(85);
        }
    }

    private String formatResult(InterpolationResult r) {
        return String.format("%-40s  f(%.4f) = %.8f",
                r.getMethodName(), r.getX(), r.getY());
    }
}
