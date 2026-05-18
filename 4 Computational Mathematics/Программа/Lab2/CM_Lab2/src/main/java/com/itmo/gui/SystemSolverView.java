package com.itmo.gui;

import com.itmo.gui.chart.ChartExporter;
import io.fair_acc.chartfx.XYChart;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.TextField;
import javafx.stage.FileChooser;
import com.itmo.core.functions.SystemInfo;
import com.itmo.core.functions.SystemRepository;
import com.itmo.io.FileUtils;
import com.itmo.core.model.SystemSolveResult;
import com.itmo.core.solvers.system.SimpleIterationSystemSolver;
import com.itmo.core.solvers.system.utils.ConvergenceCheckResult;
import com.itmo.gui.utils.SystemSolutionVerifier;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class SystemSolverView extends BaseSolverView {
    private ComboBox<String> systemComboBox;
    private TextField xField;
    private TextField yField;
    private TextField epsilonField;
    private Button fileButton;
    private final SimpleIterationSystemSolver solver;
    private List<SystemInfo> systems;
    private SystemInfo currentSystem;

    public SystemSolverView() {
        super("Решение систем нелинейных уравнений", "system_result.txt");
        this.solver = new SimpleIterationSystemSolver();
    }

    @Override
    protected String getTitleText() {
        return "Решение систем нелинейных уравнений";
    }

    @Override
    protected List<Node> createFormRows() {
        systems = SystemRepository.getAllSystems();
        List<String> sysNames = new ArrayList<>();
        for (int i = 0; i < systems.size(); i++) {
            SystemInfo sys = systems.get(i);
            sysNames.add(sys.getEq1String() + ", " + sys.getEq2String());
        }

        systemComboBox = FormBuilder.comboBox(sysNames);
        systemComboBox.setPrefWidth(600);
        xField = FormBuilder.numberField("0.5");
        yField = FormBuilder.numberField("0.5");
        epsilonField = FormBuilder.numberField("1e-3");
        fileButton = new Button("Загрузить из файла");
        fileButton.setPrefWidth(150);

        return List.of(
            FormBuilder.row().label("Система", systemComboBox).build(),
            FormBuilder.row().labelValue("Метод", solver.getMethodName()).build(),
            FormBuilder.row()
                .label("x", xField)
                .spacer().label("y", yField)
                .spacer().label("ε", epsilonField)
                .build(),
            FormBuilder.row().node(fileButton).build()
        );
    }

    @Override
    protected Button[] getExtraButtons() {
        return new Button[]{fileButton};
    }

    @Override
    protected void onShow() {
        updateSystem();
        updateChart();

        systemComboBox.setOnAction(e -> { updateSystem(); updateChart(); });
        xField.textProperty().addListener((obs, old, val) -> updateChart());
        yField.textProperty().addListener((obs, old, val) -> updateChart());
        fileButton.setOnAction(e -> loadFromFile());
    }

    @Override
    protected void solve() {
        ResultFormatter.Builder f = ResultFormatter.builder()
            .title("              РЕШЕНИЕ СИСТЕМЫ УРАВНЕНИЙ");

        try {
            int sysIndex = systemComboBox.getSelectionModel().getSelectedIndex();
            if (sysIndex < 0) {
                resultArea.setText(f.error("Выберите систему.").toString());
                return;
            }

            double xInit = GuiUtils.parseDouble(xField.getText());
            double yInit = GuiUtils.parseDouble(yField.getText());
            double epsilon = GuiUtils.parseDouble(epsilonField.getText());

            f.section(1, "ИСХОДНЫЕ ДАННЫЕ")
             .subSection("Система уравнений:");

            SystemInfo system = systems.get(sysIndex);
            f.line(system.getEq1String()).line(system.getEq2String()).blank()
             .subSection("Начальное приближение:")
             .line("x = %s", xInit).line("y = %s", yInit).blank()
             .line("Точность: ε = %s", epsilon).blank();

            if (epsilon <= 0) {
                resultArea.setText(f.error("Точность должна быть положительным числом.").toString());
                return;
            }

            f.section(2, "МЕТОД РЕШЕНИЯ").line(solver.getMethodName()).blank()
             .subSection("Итерационная схема:")
             .line(system.getPhi1String())
             .line(system.getPhi2String()).blank()
             .subSection("Условие сходимости:")
             .line("Требуется: max|φ'(x)| < 1").blank();

            ConvergenceCheckResult convCheck =
                solver.checkConvergence(system, xInit, yInit);
            f.subSection("Матрица Якоби Jφ в начальной точке:")
             .line("∂φ1/∂x = %.6f", convCheck.dphi1dx)
             .line("∂φ1/∂y = %.6f", convCheck.dphi1dy)
             .line("∂φ2/∂x = %.6f", convCheck.dphi2dx)
             .line("∂φ2/∂y = %.6f", convCheck.dphi2dy).blank()
             .line("max|φ'(x₀)| = %.6f", convCheck.jacobianNorm)
             .line("Условие max|φ'(x)| < 1: %s", convCheck.conditionMet ? "ВЫПОЛНЕНО ✓" : "НЕ ВЫПОЛНЕНО ✗").blank()
             .subSection("Начальные значения функций:")
             .line("f1(%s, %s) = %s", xInit, yInit, system.getF1().evaluate(xInit, yInit))
             .line("f2(%s, %s) = %s", xInit, yInit, system.getF2().evaluate(xInit, yInit));

            f.section(3, "ИТЕРАЦИОННЫЙ ПРОЦЕСС");

            SystemSolveResult result = solver.solve(system, xInit, yInit, epsilon);
            f.line(result.getMessage()).blank();

            f.section(4, "РЕЗУЛЬТАТ");

            if (result.isConverged()) {
                f.line("✓ Метод сошелся").blank()
                 .subSection("Найденное решение:")
                 .line("x = %s", result.getX1())
                 .line("y = %s", result.getX2()).blank()
                 .subSection("Значения функций в найденной точке:")
                 .line("f1(x, y) = %s", result.getF1Value())
                 .line("f2(x, y) = %s", result.getF2Value()).blank()
                 .line("Количество итераций: %s", result.getIterations()).blank()
                 .subSection("Погрешность (последняя итерация):");
                double[] errors = result.getErrors();
                if (errors.length > 0) {
                    f.line("max|xᵢ⁽ᵏ⁾ - xᵢ⁽ᵏ⁻¹⁾| = %s", errors[errors.length - 1]);
                }

                f.blank().section(5, "ПРОВЕРКА РЕШЕНИЯ");
                double[] verification = SystemSolutionVerifier.verify(system, result.getX1(), result.getX2());
                f.subSection("Подстановка решения в исходную систему:")
                 .line("f1(%.6f, %.6f) = %.10f", result.getX1(), result.getX2(), verification[0])
                 .line("f2(%.6f, %.6f) = %.10f", result.getX1(), result.getX2(), verification[1]).blank()
                 .subSection("Проверка: |f(x)| < ε");
                boolean v1ok = Math.abs(verification[0]) < epsilon;
                boolean v2ok = Math.abs(verification[1]) < epsilon;
                f.checkResult("|f1|", Math.abs(verification[0]), epsilon);
                f.checkResult("|f2|", Math.abs(verification[1]), epsilon);
                f.blank().line("Результат проверки: %s", (v1ok && v2ok ? "Решение КОРРЕКТНО ✓" : "Решение НЕ КОРРЕКТНО ✗"));
            } else {
                f.line("✗ Метод НЕ сошелся").blank()
                 .line("Причина: %s", result.getMessage()).blank()
                 .subSection("Последнее приближение:")
                 .line("x = %s", result.getX1())
                 .line("y = %s", result.getX2()).blank()
                 .subSection("Значения функций:")
                 .line("f1 = %s", result.getF1Value())
                 .line("f2 = %s", result.getF2Value()).blank()
                 .line("Итераций: %s", result.getIterations());
            }

            resultArea.setText(f.build());
            updateChart();

        } catch (NumberFormatException e) {
            resultArea.setText(f.blank().error("Неверный формат числа.").toString());
        } catch (Exception e) {
            resultArea.setText(f.blank().error(e.getMessage()).toString());
        }
    }

    private void updateSystem() {
        int index = systemComboBox.getSelectionModel().getSelectedIndex();
        if (index >= 0 && index < systems.size()) {
            currentSystem = systems.get(index);
        }
    }

    private void updateChart() {
        if (currentSystem == null) return;
        try {
            double x1 = GuiUtils.parseDouble(xField.getText());
            double x2 = GuiUtils.parseDouble(yField.getText());
            XYChart chart = ChartExporter.createSystemChart(currentSystem, x1, x2);
            updateChart(chart);
        } catch (Exception ignored) {}
    }

    private void loadFromFile() {
        FileChooser fc = new FileChooser();
        fc.setTitle("Загрузить данные");
        File file = fc.showOpenDialog(stage);
        if (file != null) {
            try {
                String[] data = FileUtils.readData(file, 3);
                xField.setText(data[0]);
                yField.setText(data[1]);
                epsilonField.setText(data[2]);
                resultArea.setText(ResultFormatter.builder()
                    .line("Данные загружены из файла:")
                    .line("  x = %s", data[0])
                    .line("  y = %s", data[1])
                    .line("  ε = %s", data[2]).toString());
            } catch (Exception e) {
                showError("Ошибка загрузки файла: " + e.getMessage());
            }
        }
    }
}
