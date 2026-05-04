package org.example.gui;

import org.example.engine.LSMSolver;
import org.example.model.ApproximationResult;

import javax.swing.*;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.*;
import java.util.ArrayList;
import java.util.List;

public class MainFrame extends JFrame {

    private JTable inputTable;
    private DefaultTableModel inputModel;
    private JTextArea resultArea;
    private ChartPanel chartPanel;
    private JTabbedPane tabbedPane;

    public MainFrame() {
        setTitle("LSM函数逼近 - 最小二乘法");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 850);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        tabbedPane = new JTabbedPane();

        JPanel inputPanel = createInputPanel();
        tabbedPane.addTab("数据输入", inputPanel);

        JPanel resultPanel = createResultPanel();
        tabbedPane.addTab("计算结果", resultPanel);

        chartPanel = new ChartPanel();
        tabbedPane.addTab("图形", chartPanel);

        add(tabbedPane, BorderLayout.CENTER);

        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 5));
        JButton calcBtn = new JButton("计算");
        JButton loadBtn = new JButton("加载数据");
        JButton saveBtn = new JButton("保存结果");
        JButton clearBtn = new JButton("清空");

        String btnFont = "Microsoft YaHei";
        calcBtn.setFont(new Font(btnFont, Font.BOLD, 14));
        loadBtn.setFont(new Font(btnFont, Font.PLAIN, 14));
        saveBtn.setFont(new Font(btnFont, Font.PLAIN, 14));
        clearBtn.setFont(new Font(btnFont, Font.PLAIN, 14));

        calcBtn.addActionListener(this::onCalculate);
        loadBtn.addActionListener(this::onLoad);
        saveBtn.addActionListener(this::onSave);
        clearBtn.addActionListener(this::onClear);

        buttonPanel.add(calcBtn);
        buttonPanel.add(loadBtn);
        buttonPanel.add(saveBtn);
        buttonPanel.add(clearBtn);

        add(buttonPanel, BorderLayout.SOUTH);

        initDefaultData();
    }

    private JPanel createInputPanel() {
        JPanel panel = new JPanel(new BorderLayout());

        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel lbl = new JLabel("请输入数据点 (至少8个点，建议8-12个):");
        lbl.setFont(new Font("Microsoft YaHei", Font.PLAIN, 13));
        topPanel.add(lbl);
        JButton addRowBtn = new JButton("添加行");
        addRowBtn.setFont(new Font("Microsoft YaHei", Font.PLAIN, 13));
        addRowBtn.addActionListener(e -> inputModel.addRow(new Object[]{inputModel.getRowCount(), 0.0, 0.0}));
        topPanel.add(addRowBtn);

        JButton removeRowBtn = new JButton("删除选中行");
        removeRowBtn.setFont(new Font("Microsoft YaHei", Font.PLAIN, 13));
        removeRowBtn.addActionListener(e -> {
            int row = inputTable.getSelectedRow();
            if (row >= 0) inputModel.removeRow(row);
        });
        topPanel.add(removeRowBtn);

        panel.add(topPanel, BorderLayout.NORTH);

        inputModel = new DefaultTableModel(new Object[]{"序号", "x", "y"}, 0) {
            @Override
            public Class<?> getColumnClass(int columnIndex) {
                return columnIndex == 0 ? Integer.class : Double.class;
            }
        };

        inputTable = new JTable(inputModel);
        inputTable.setFont(new Font("Consolas", Font.PLAIN, 13));
        inputTable.getColumnModel().getColumn(0).setPreferredWidth(50);
        inputTable.getColumnModel().getColumn(1).setPreferredWidth(100);
        inputTable.getColumnModel().getColumn(2).setPreferredWidth(100);

        JScrollPane scroll = new JScrollPane(inputTable);
        scroll.setPreferredSize(new Dimension(400, 500));
        panel.add(scroll, BorderLayout.CENTER);
        return panel;
    }

    private JPanel createResultPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        resultArea = new JTextArea();
        resultArea.setFont(new Font("Consolas", Font.PLAIN, 13));
        resultArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(resultArea);
        panel.add(scroll, BorderLayout.CENTER);
        return panel;
    }

    private void initDefaultData() {
        // Option 14: y = 25x / (x^4 + 14), x in [0, 4], h = 0.4
        double[] xVals = {0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0};
        for (int i = 0; i < xVals.length; i++) {
            double xi = xVals[i];
            double yi = 25.0 * xi / (xi * xi * xi * xi + 14.0);
            inputModel.addRow(new Object[]{i + 1, xi, yi});
        }
    }

    private List<Double> getXValues() {
        List<Double> list = new ArrayList<>();
        for (int i = 0; i < inputModel.getRowCount(); i++) {
            Object val = inputModel.getValueAt(i, 1);
            if (val instanceof Double) list.add((Double) val);
            else if (val instanceof String) {
                try { list.add(Double.parseDouble((String) val)); } catch (NumberFormatException ignored) {}
            }
        }
        return list;
    }

    private List<Double> getYValues() {
        List<Double> list = new ArrayList<>();
        for (int i = 0; i < inputModel.getRowCount(); i++) {
            Object val = inputModel.getValueAt(i, 2);
            if (val instanceof Double) list.add((Double) val);
            else if (val instanceof String) {
                try { list.add(Double.parseDouble((String) val)); } catch (NumberFormatException ignored) {}
            }
        }
        return list;
    }

    private void onCalculate(ActionEvent e) {
        List<Double> xVals = getXValues();
        List<Double> yVals = getYValues();

        if (xVals.size() < 8) {
            JOptionPane.showMessageDialog(this, "至少需要8个数据点", "错误", JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (xVals.size() != yVals.size()) {
            JOptionPane.showMessageDialog(this, "x和y数据点数不一致", "错误", JOptionPane.ERROR_MESSAGE);
            return;
        }

        List<ApproximationResult> results = LSMSolver.computeAll(xVals, yVals);

        StringBuilder sb = new StringBuilder();
        sb.append("==================== 最小二乘法逼近结果 ====================\n\n");
        sb.append(String.format("数据点数: %d\n\n", xVals.size()));

        // Find best
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

            // Detailed table
            sb.append("\n  数据点详情:\n");
            sb.append(String.format("  %6s %12s %12s %12s %12s\n", "x", "y", "phi(x)", "epsilon", "|eps|"));
            sb.append("  ---------------------------------------------------------\n");
            double[] yPred = r.getYPredicted();
            double[] res = r.getResiduals();
            for (int i = 0; i < xVals.size(); i++) {
                sb.append(String.format("  %6.2f %12.4f %12.4f %12.4f %12.4f\n",
                        xVals.get(i), yVals.get(i), yPred[i], res[i], Math.abs(res[i])));
            }
            sb.append("\n");
        }

        sb.append("==============================================================\n");
        if (best != null) {
            sb.append(String.format("\n★ 最佳逼近: 【%s】\n", best.getFunctionType()));
            sb.append(String.format("  公式: %s\n", best.getFormula()));
            sb.append(String.format("  均方根偏差: %.6f\n", best.getDelta()));
        }

        resultArea.setText(sb.toString());
        chartPanel.setData(xVals, yVals, results);
        tabbedPane.setSelectedIndex(2); // switch to chart
    }

    private void onLoad(ActionEvent e) {
        JFileChooser chooser = new JFileChooser();
        if (chooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File file = chooser.getSelectedFile();
            inputModel.setRowCount(0);
            try (BufferedReader br = new BufferedReader(
                    new InputStreamReader(new FileInputStream(file), "UTF-8"))) {
                String line;
                int row = 0;
                while ((line = br.readLine()) != null) {
                    String[] parts = line.trim().split("[,\\s]+");
                    if (parts.length >= 2) {
                        try {
                            double x = Double.parseDouble(parts[0]);
                            double y = Double.parseDouble(parts[1]);
                            inputModel.addRow(new Object[]{++row, x, y});
                        } catch (NumberFormatException ignored) {}
                    }
                }
                JOptionPane.showMessageDialog(this, "成功加载 " + row + " 个数据点");
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "读取文件失败: " + ex.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void onSave(ActionEvent e) {
        JFileChooser chooser = new JFileChooser();
        if (chooser.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
            File file = chooser.getSelectedFile();
            try (PrintWriter pw = new PrintWriter(
                    new OutputStreamWriter(new FileOutputStream(file), "UTF-8"))) {
                pw.print(resultArea.getText());
                JOptionPane.showMessageDialog(this, "结果已保存到 " + file.getName());
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "保存失败: " + ex.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void onClear(ActionEvent e) {
        inputModel.setRowCount(0);
        resultArea.setText("");
        chartPanel.clear();
    }
}
