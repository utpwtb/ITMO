package com.itmo.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.text.DecimalFormat;

/**
 * Displays computed results in a JTable (bottom-left area).
 */
public class ResultTablePanel extends JPanel {

    private final JTable table;
    private final DefaultTableModel tableModel;
    private final JTextArea errorArea;
    private final DecimalFormat df = new DecimalFormat("0.000000");

    public ResultTablePanel() {
        setLayout(new BorderLayout());
        setBorder(BorderFactory.createTitledBorder("Results"));

        tableModel = new DefaultTableModel();
        table = new JTable(tableModel);
        table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.setPreferredSize(new Dimension(500, 300));
        add(scrollPane, BorderLayout.CENTER);

        errorArea = new JTextArea(5, 40);
        errorArea.setEditable(false);
        errorArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        JScrollPane errorScroll = new JScrollPane(errorArea);
        errorScroll.setBorder(BorderFactory.createTitledBorder("Error Estimates"));
        add(errorScroll, BorderLayout.SOUTH);
    }

    public void clear() {
        tableModel.setRowCount(0);
        tableModel.setColumnCount(0);
        errorArea.setText("");
    }

    /**
     * Populate table with results from multiple methods.
     * exactX/exactY = exact solution at each node.
     */
    public void displayResults(String[] methodNames, double[][] allY,
                               double[] x, double[] exactY) {
        clear();
        int cols = 2 + allY.length + 1; // i, xi, method1, method2, ..., exact
        String[] colNames = new String[cols];
        colNames[0] = "i";
        colNames[1] = "xi";
        for (int m = 0; m < allY.length; m++) {
            colNames[2 + m] = methodNames[m];
        }
        colNames[cols - 1] = "Exact";

        for (String name : colNames) {
            tableModel.addColumn(name);
        }

        int n = x.length - 1;
        for (int i = 0; i <= n; i++) {
            Object[] row = new Object[cols];
            row[0] = i;
            row[1] = df.format(x[i]);
            for (int m = 0; m < allY.length; m++) {
                row[2 + m] = df.format(allY[m][i]);
            }
            row[cols - 1] = df.format(exactY[i]);
            tableModel.addRow(row);
        }
    }

    public void displayErrors(String[] methodNames, double[] errors,
                              String[] errorTypes) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < methodNames.length; i++) {
            sb.append(methodNames[i]).append(":\n");
            if ("runge".equals(errorTypes[i])) {
                sb.append("  Runge rule estimate: ").append(String.format("%.8f", errors[i])).append("\n");
            } else {
                sb.append("  max|y_exact - y_i| = ").append(String.format("%.8f", errors[i])).append("\n");
            }
        }
        errorArea.setText(sb.toString());
    }
}
