package com.itmo.gui;

import com.itmo.ode.ODE;
import com.itmo.ode.ODE1;
import com.itmo.ode.ODE2;
import com.itmo.ode.ODE3;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionListener;

/**
 * Top input panel: ODE selection, parameters, method checkboxes, compute button.
 */
public class InputPanel extends JPanel {

    private final JComboBox<String> odeCombo;
    private final JTextField x0Field, y0Field, xnField, hField, epsField;
    private final JCheckBox eulerCheck, rk4Check, milneCheck;
    private final JButton computeButton;

    private final ODE[] odes = { new ODE1(), new ODE2(), new ODE3() };

    public InputPanel() {
        setLayout(new GridBagLayout());
        setBorder(BorderFactory.createTitledBorder("Входные данные"));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(4, 6, 4, 6);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Row 0: ODE selection
        gbc.gridy = 0;
        gbc.gridx = 0;
        add(new JLabel("Уравнение:"), gbc);
        gbc.gridx = 1;
        gbc.gridwidth = 5;
        odeCombo = new JComboBox<>();
        for (ODE ode : odes) {
            odeCombo.addItem(ode.expression());
        }
        add(odeCombo, gbc);

        // Row 1: x0, y0, xn
        gbc.gridwidth = 1;
        gbc.gridy = 1;

        gbc.gridx = 0;
        add(new JLabel("x\u2080:"), gbc);
        gbc.gridx = 1;
        x0Field = new JTextField("0", 6);
        add(x0Field, gbc);

        gbc.gridx = 2;
        add(new JLabel("y\u2080:"), gbc);
        gbc.gridx = 3;
        y0Field = new JTextField("1", 6);
        add(y0Field, gbc);

        gbc.gridx = 4;
        add(new JLabel("xn:"), gbc);
        gbc.gridx = 5;
        xnField = new JTextField("2", 6);
        add(xnField, gbc);

        // Row 2: h, ε
        gbc.gridy = 2;

        gbc.gridx = 0;
        add(new JLabel("h:"), gbc);
        gbc.gridx = 1;
        hField = new JTextField("0.2", 6);
        add(hField, gbc);

        gbc.gridx = 2;
        add(new JLabel("\u03b5:"), gbc);
        gbc.gridx = 3;
        epsField = new JTextField("0.001", 6);
        add(epsField, gbc);

        // Row 3: methods and button
        gbc.gridy = 3;
        gbc.gridx = 0;
        add(new JLabel("Методы:"), gbc);
        gbc.gridx = 1;
        eulerCheck = new JCheckBox("Модифицированный Эйлер", true);
        add(eulerCheck, gbc);
        gbc.gridx = 2;
        rk4Check = new JCheckBox("Рунге-Кутта 4", true);
        add(rk4Check, gbc);
        gbc.gridx = 3;
        milneCheck = new JCheckBox("Милн", true);
        add(milneCheck, gbc);

        gbc.gridx = 5;
        computeButton = new JButton("Вычислить");
        add(computeButton, gbc);
    }

    public void onCompute(ActionListener listener) {
        computeButton.addActionListener(listener);
    }

    public ODE getSelectedODE() {
        return odes[odeCombo.getSelectedIndex()];
    }

    public double getX0() { return Double.parseDouble(x0Field.getText()); }
    public double getY0() { return Double.parseDouble(y0Field.getText()); }
    public double getXn() { return Double.parseDouble(xnField.getText()); }
    public double getH()  { return Double.parseDouble(hField.getText()); }
    public double getEps(){ return Double.parseDouble(epsField.getText()); }

    public boolean useEuler() { return eulerCheck.isSelected(); }
    public boolean useRK4()   { return rk4Check.isSelected(); }
    public boolean useMilne() { return milneCheck.isSelected(); }
}
