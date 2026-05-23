package org.example.gui;

import org.example.model.ApproximationResult;
import org.example.service.ApproximationService;

import javax.swing.*;
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
    private JPanel legendPanel;

    private static final Font UI_FONT = new Font("Microsoft YaHei", Font.PLAIN, 13);
    private static final Font MONO_FONT = new Font("Consolas", Font.PLAIN, 13);
    private static final Font RESULT_FONT = new Font("Microsoft YaHei", Font.PLAIN, 13);

    public MainFrame() {
        setTitle("Аппроксимация МНК");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1300, 850);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(5, 0));

        JPanel leftPanel = createLeftPanel();
        leftPanel.setPreferredSize(new Dimension(380, 850));
        leftPanel.setMinimumSize(new Dimension(300, 600));

        JSplitPane rightSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT);
        rightSplit.setResizeWeight(0.5);
        rightSplit.setTopComponent(createResultPanel());

        chartPanel = new ChartPanel();
        JPanel chartContainer = new JPanel(new BorderLayout(0, 2));
        legendPanel = createLegendPanel();
        chartContainer.add(legendPanel, BorderLayout.NORTH);
        chartContainer.add(chartPanel, BorderLayout.CENTER);
        rightSplit.setBottomComponent(chartContainer);

        mainPanel.add(leftPanel, BorderLayout.WEST);
        mainPanel.add(rightSplit, BorderLayout.CENTER);

        add(mainPanel);
        initDefaultData();
    }

    private JPanel createLeftPanel() {
        JPanel panel = new JPanel(new BorderLayout(5, 5));
        panel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        JLabel lbl = new JLabel("<html>Введите точки данных (минимум 8, рекомендуется 8-12):</html>");
        lbl.setFont(UI_FONT);
        panel.add(lbl, BorderLayout.NORTH);

        inputModel = new DefaultTableModel(new Object[]{"№", "x", "y"}, 0) {
            @Override
            public Class<?> getColumnClass(int columnIndex) {
                return columnIndex == 0 ? Integer.class : String.class;
            }
        };

        inputTable = new JTable(inputModel);
        inputTable.setFont(MONO_FONT);
        inputTable.setRowHeight(22);
        inputTable.getColumnModel().getColumn(0).setPreferredWidth(40);
        inputTable.getColumnModel().getColumn(0).setMaxWidth(60);
        inputTable.getColumnModel().getColumn(1).setPreferredWidth(120);
        inputTable.getColumnModel().getColumn(2).setPreferredWidth(120);

        JScrollPane tableScroll = new JScrollPane(inputTable);
        panel.add(tableScroll, BorderLayout.CENTER);

        JPanel buttonPanel = new JPanel(new GridLayout(0, 2, 5, 5));
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(5, 0, 0, 0));

        JButton addRowBtn = new JButton("Добавить");
        JButton removeRowBtn = new JButton("Удалить");
        JButton calcBtn = new JButton("Вычислить");
        JButton loadBtn = new JButton("Загрузить");
        JButton saveBtn = new JButton("Сохранить");
        JButton clearBtn = new JButton("Очистить");

        for (JButton btn : new JButton[]{addRowBtn, removeRowBtn, calcBtn, loadBtn, saveBtn, clearBtn}) {
            btn.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        }

        addRowBtn.addActionListener(e -> inputModel.addRow(new Object[]{inputModel.getRowCount() + 1, "", ""}));
        removeRowBtn.addActionListener(e -> {
            int row = inputTable.getSelectedRow();
            if (row >= 0) {
                inputModel.removeRow(row);
                for (int i = 0; i < inputModel.getRowCount(); i++) {
                    inputModel.setValueAt(i + 1, i, 0);
                }
            }
        });
        calcBtn.addActionListener(this::onCalculate);
        loadBtn.addActionListener(this::onLoad);
        saveBtn.addActionListener(this::onSave);
        clearBtn.addActionListener(this::onClear);

        buttonPanel.add(addRowBtn);
        buttonPanel.add(removeRowBtn);
        buttonPanel.add(calcBtn);
        buttonPanel.add(loadBtn);
        buttonPanel.add(saveBtn);
        buttonPanel.add(clearBtn);

        panel.add(buttonPanel, BorderLayout.SOUTH);
        return panel;
    }

    private JScrollPane createResultPanel() {
        resultArea = new JTextArea();
        resultArea.setFont(RESULT_FONT);
        resultArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(resultArea);
        scroll.setBorder(BorderFactory.createTitledBorder("Результаты"));
        return scroll;
    }

    private JPanel createLegendPanel() {
        JPanel panel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                List<ApproximationResult> r = chartPanel.getResults();
                Graphics2D g2 = (Graphics2D) g;
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));

                int x = 10;
                int y = getHeight() / 2 + 5;

                Color[] colors = ChartPanel.getColors();

                g2.setColor(Color.BLACK);
                g2.fillOval(x, y - 4, 8, 8);
                g2.drawString("Исходные данные", x + 14, y + 4);
                x += 150;

                if (r != null) {
                    for (int idx = 0; idx < r.size(); idx++) {
                        ApproximationResult res = r.get(idx);
                        if (res.getDelta() >= Double.MAX_VALUE) continue;
                        g2.setColor(colors[idx % colors.length]);
                        g2.fillOval(x, y - 4, 8, 8);
                        g2.setColor(Color.BLACK);
                        g2.drawString(res.getFunctionType(), x + 14, y + 4);
                        x += g2.getFontMetrics().stringWidth(res.getFunctionType()) + 40;
                    }
                }
            }
        };
        panel.setPreferredSize(new Dimension(0, 40));
        panel.setBackground(Color.WHITE);
        return panel;
    }

    private void initDefaultData() {
        double[] xVals = {0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0};
        for (int i = 0; i < xVals.length; i++) {
            double xi = xVals[i];
            double yi = 25.0 * xi / (xi * xi * xi * xi + 14.0);
            inputModel.addRow(new Object[]{i + 1, String.valueOf(xi), String.valueOf(yi)});
        }
    }

    private double parseNumber(Object val) {
        if (val == null) return Double.NaN;
        String s = val.toString().trim();
        if (s.isEmpty()) return Double.NaN;
        s = s.replace(',', '.');
        s = s.replaceAll("\\s+", "");
        try {
            return Double.parseDouble(s);
        } catch (NumberFormatException e) {
            return Double.NaN;
        }
    }

    private List<Double> getXValues() {
        List<Double> list = new ArrayList<>();
        for (int i = 0; i < inputModel.getRowCount(); i++) {
            double val = parseNumber(inputModel.getValueAt(i, 1));
            if (!Double.isNaN(val)) list.add(val);
        }
        return list;
    }

    private List<Double> getYValues() {
        List<Double> list = new ArrayList<>();
        for (int i = 0; i < inputModel.getRowCount(); i++) {
            double val = parseNumber(inputModel.getValueAt(i, 2));
            if (!Double.isNaN(val)) list.add(val);
        }
        return list;
    }

    private void onCalculate(ActionEvent e) {
        List<Double> xVals = getXValues();
        List<Double> yVals = getYValues();

        int validCount = Math.min(xVals.size(), yVals.size());
        if (validCount < 8) {
            JOptionPane.showMessageDialog(this,
                    "Необходимо минимум 8 точек. Текущее количество: " + validCount,
                    "Ошибка", JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (xVals.size() != yVals.size()) {
            JOptionPane.showMessageDialog(this,
                    "Количество x и y не совпадает (x: " + xVals.size() + ", y: " + yVals.size() + ")",
                    "Ошибка", JOptionPane.ERROR_MESSAGE);
            return;
        }

        int n = Math.min(xVals.size(), yVals.size());
        xVals = xVals.subList(0, n);
        yVals = yVals.subList(0, n);

        List<ApproximationResult> results = ApproximationService.computeAll(xVals, yVals);

        StringBuilder sb = new StringBuilder();
        sb.append("==================== Результаты аппроксимации МНК ====================\n\n");
        sb.append(String.format("Количество точек: %d\n\n", xVals.size()));

        ApproximationResult best = null;
        double minDelta = Double.MAX_VALUE;

        for (ApproximationResult r : results) {
            if (r.getDelta() < minDelta) {
                minDelta = r.getDelta();
                best = r;
            }

            sb.append("--------------------------------------------------------------\n");
            sb.append(String.format("%s\n", r.getFunctionType()));
            sb.append(String.format("  Формула: %s\n", ApproximationService.getFormula(r)));
            if (r.getS() >= Double.MAX_VALUE / 2) {
                sb.append("  Мера отклонения S = N/A (невозможно)\n");
                sb.append("  Среднекв. отклонение = N/A (невозможно)\n");
            } else {
                sb.append(String.format("  Мера отклонения S = %.6f\n", r.getS()));
                sb.append(String.format("  Среднекв. отклонение = %.6f\n", r.getDelta()));
            }
            sb.append(String.format("  Коэффициент детерминации R² = %.6f\n", r.getR2()));
            sb.append(String.format("  Оценка: %s\n", r.getR2Message()));

            if (r.getFunctionType().contains("Линейная")) {
                sb.append(String.format("  Коэффициент корреляции Пирсона r = %.6f\n", r.getPearsonR()));
            }

            sb.append("\n  Детали точек:\n");
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
            sb.append(String.format("\n  Лучшая аппроксимация: %s\n", best.getFunctionType()));
            sb.append(String.format("  Формула: %s\n", ApproximationService.getFormula(best)));
            sb.append(String.format("  Среднекв. отклонение: %.6f\n", best.getDelta()));
        }

        resultArea.setText(sb.toString());
        resultArea.setCaretPosition(0);
        chartPanel.setData(xVals, yVals, results);
        legendPanel.repaint();
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
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) continue;
                    String[] parts = line.split("[;\\s]+");
                    if (parts.length >= 2) {
                        double x = parseNumber(parts[0]);
                        double y = parseNumber(parts[1]);
                        if (!Double.isNaN(x) && !Double.isNaN(y)) {
                            inputModel.addRow(new Object[]{++row, parts[0].trim(), parts[1].trim()});
                        }
                    }
                }
                JOptionPane.showMessageDialog(this, "Загружено " + row + " точек");
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "Ошибка чтения файла: " + ex.getMessage(),
                        "Ошибка", JOptionPane.ERROR_MESSAGE);
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
                JOptionPane.showMessageDialog(this, "Результат сохранён в " + file.getName());
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "Ошибка сохранения: " + ex.getMessage(),
                        "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void onClear(ActionEvent e) {
        inputModel.setRowCount(0);
        resultArea.setText("");
        chartPanel.clear();
        legendPanel.repaint();
    }
}
