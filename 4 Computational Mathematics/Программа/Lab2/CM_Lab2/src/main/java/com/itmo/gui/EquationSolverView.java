package com.itmo.gui;

import com.itmo.gui.chart.ChartExporter;
import io.fair_acc.chartfx.XYChart;
import javafx.scene.Node;
import javafx.scene.control.*;
import javafx.stage.FileChooser;
import com.itmo.core.functions.EquationInfo;
import com.itmo.core.functions.EquationRepository;
import com.itmo.io.FileUtils;
import com.itmo.core.model.RootCheckResult;
import com.itmo.core.model.SolveResult;
import com.itmo.core.solvers.equation.EquationSolver;
import com.itmo.core.solvers.equation.utils.IntervalRootChecker;
import com.itmo.core.solvers.equation.ChordMethodSolver;
import com.itmo.core.solvers.equation.SimpleIterationMethodSolver;
import com.itmo.core.solvers.equation.SecantMethodSolver;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class EquationSolverView extends BaseSolverView {
    private ComboBox<String> equationComboBox;
    private ComboBox<String> methodComboBox;
    private TextField aField;
    private TextField bField;
    private TextField epsilonField;
    private Button fileButton;
    private List<EquationInfo> equations;
    private EquationInfo currentEquation;

    private static final String[] METHOD_NAMES = {"Метод хорд", "Метод секущих", "Метод простой итерации"};

    public EquationSolverView() {
        super("Решение нелинейных уравнений", "result.txt");
    }

    @Override
    protected String getTitleText() {
        return "Решение нелинейных уравнений";
    }

    @Override
    protected List<Node> createFormRows() {
        equations = EquationRepository.getAllEquations();
        List<String> eqNames = new ArrayList<>();
        for (int i = 0; i < equations.size(); i++) {
            eqNames.add((i + 1) + ". " + equations.get(i).getName());
        }

        equationComboBox = FormBuilder.comboBox(eqNames);
        equationComboBox.setPrefWidth(400);
        methodComboBox = FormBuilder.comboBox(METHOD_NAMES);
        methodComboBox.setPrefWidth(200);
        aField = FormBuilder.numberField("0.0");
        bField = FormBuilder.numberField("3.0");
        epsilonField = FormBuilder.numberField("1e-3");
        fileButton = new Button("Загрузить из файла");
        fileButton.setPrefWidth(150);

        return List.of(
            FormBuilder.row().label("Уравнение", equationComboBox).build(),
            FormBuilder.row().label("Метод", methodComboBox).build(),
            FormBuilder.row()
                .label("a", aField)
                .spacer().label("b", bField)
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
        updateEquation();
        updateChart();

        equationComboBox.setOnAction(e -> { updateEquation(); updateChart(); });
        aField.textProperty().addListener((obs, old, val) -> { try { GuiUtils.parseDouble(val); updateChart(); } catch (Exception ignored) {} });
        bField.textProperty().addListener((obs, old, val) -> { try { GuiUtils.parseDouble(val); updateChart(); } catch (Exception ignored) {} });
        fileButton.setOnAction(e -> loadFromFile());
    }

    @Override
    protected void solve() {
        ResultFormatter.Builder f = ResultFormatter.builder()
            .title("                    РЕШЕНИЕ УРАВНЕНИЯ");

        try {
            int eqIndex = equationComboBox.getSelectionModel().getSelectedIndex();
            int methodIndex = methodComboBox.getSelectionModel().getSelectedIndex();

            if (eqIndex < 0 || methodIndex < 0) {
                resultArea.setText(f.error("Выберите уравнение и метод.").toString());
                return;
            }

            double a = GuiUtils.parseDouble(aField.getText());
            double b = GuiUtils.parseDouble(bField.getText());
            double epsilon = GuiUtils.parseDouble(epsilonField.getText());

            f.section(1, "ИСХОДНЫЕ ДАННЫЕ")
             .line("Уравнение: %s", equations.get(eqIndex).getEquationString())
             .line("Интервал: [%s, %s]", a, b)
             .line("Точность: %s", epsilon).blank();

            if (a >= b) { resultArea.setText(f.error("Левая граница должна быть меньше правой.").toString()); return; }
            if (epsilon <= 0) { resultArea.setText(f.error("Точность должна быть положительным числом.").toString()); return; }

            EquationInfo equation = equations.get(eqIndex);

            f.section(2, "ПРОВЕРКА НАЛИЧИЯ КОРНЯ")
             .line("Анализ интервала [%s, %s]:", a, b)
             .line("f(a) = %s", equation.getFunction().evaluate(a))
             .line("f(b) = %s", equation.getFunction().evaluate(b));

            IntervalRootChecker rootChecker = new IntervalRootChecker();
            RootCheckResult checkResult = rootChecker.checkRoot(equation.getFunction(), a, b, 1000);

            if (!checkResult.hasRoot()) {
                resultArea.setText(f.blank().line("РЕЗУЛЬТАТ: Корней на интервале НЕТ").line(checkResult.getMessage()).build());
                return;
            }
            if (checkResult.getRootCount() > 1) {
                resultArea.setText(f.blank().line("РЕЗУЛЬТАТ: Несколько корней на интервале")
                    .line("Количество корней: %s", checkResult.getRootCount())
                    .line("Рекомендация: Уточните интервал для изоляции одного корня.").build());
                return;
            }

            f.line("f(a) * f(b) < 0: Да (смена знака)")
             .line("РЕЗУЛЬТАТ: Один корень на интервале ✓").blank();

            EquationSolver[] solvers = {new ChordMethodSolver(), new SecantMethodSolver(), new SimpleIterationMethodSolver()};
            EquationSolver solver = solvers[methodIndex];
            String methodName = METHOD_NAMES[methodIndex];

            f.section(3, "МЕТОД РЕШЕНИЯ").line(methodName).blank();

            if (methodIndex == 2) {
                if (!appendNewtonRuleInfo(f, equation, a, b)) {
                    resultArea.setText(f.build());
                    return;
                }
                if (!appendIterationFunctionInfo(f, equation, a, b)) {
                    resultArea.setText(f.blank().line("РЕЗУЛЬТАТ: Метод НЕ может быть применен").build());
                    return;
                }
            }
            if (methodIndex == 1) {
                if (!appendNewtonRuleInfo(f, equation, a, b)) {
                    resultArea.setText(f.build());
                    return;
                }
            }

            f.section(4, "ИТЕРАЦИОННЫЙ ПРОЦЕСС");

            SolveResult result = solver.solve(equation.getFunction(), equation.getDerivative(), equation.getSecondDerivative(), a, b, epsilon);
            f.line(result.getMessage()).blank();

            f.section(5, "РЕЗУЛЬТАТ");

            if (result.isConverged()) {
                f.line("✓ Метод сошелся").blank()
                 .subSection("Найденный корень:")
                 .line("x = %s", result.getRoot())
                 .line("f(x) = %s", result.getFunctionValue())
                 .successCheck(Math.abs(result.getFunctionValue()) < epsilon, "|f(x)| < ε").blank()
                 .line("Количество итераций: %s", result.getIterations()).blank()
                 .subSection("Проверка решения:")
                 .line("|f(x)| = %s", Math.abs(result.getFunctionValue()))
                 .line("ε = %s", epsilon)
                 .successCheck(Math.abs(result.getFunctionValue()) < epsilon, "|f(x)| < ε");
            } else {
                f.line("✗ Метод НЕ сошелся").blank()
                 .line("Причина: %s", result.getMessage())
                 .line("Последнее приближение: x = %s", result.getRoot())
                 .line("f(x) = %s", result.getFunctionValue())
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

    private boolean appendNewtonRuleInfo(ResultFormatter.Builder f, EquationInfo equation, double a, double b) {
        double fa = equation.getFunction().evaluate(a), d2fa = equation.getSecondDerivative().evaluate(a);
        double fb = equation.getFunction().evaluate(b), d2fb = equation.getSecondDerivative().evaluate(b);

        f.subSection("Выбор начального приближения x₀ (правило Ньютона):")
         .line("f''(a) = %s", d2fa)
         .line("f''(b) = %s", d2fb)
         .line("f(a)·f''(a) = %s", fa * d2fa)
         .line("f(b)·f''(b) = %s", fb * d2fb).blank();

        if (fa * d2fa > 0) {
            f.line("Выбрано: x₀ = a (условие f(a)·f''(a) > 0 выполняется)");
        } else if (fb * d2fb > 0) {
            f.line("Выбрано: x₀ = b (условие f(b)·f''(b) > 0 выполняется)");
        } else {
            f.line("Условие f(x₀)·f''(x₀) > 0 НЕ выполняется ни на a, ни на b")
             .blank().line("Метод НЕ может быть применен — невозможно гарантировать сходимость");
            return false;
        }
        return true;
    }

    private boolean appendIterationFunctionInfo(ResultFormatter.Builder f, EquationInfo equation, double a, double b) {
        int checkPoints = 20;
        double h = (b - a) / checkPoints;
        boolean fPrimePositive = true;
        boolean fPrimeNegative = true;
        double maxAbsDf = 0;
        for (int i = 0; i <= checkPoints; i++) {
            double x = a + i * h;
            double dfVal = equation.getDerivative().evaluate(x);
            maxAbsDf = Math.max(maxAbsDf, Math.abs(dfVal));
            if (dfVal > 0) fPrimeNegative = false;
            if (dfVal < 0) fPrimePositive = false;
        }

        if (!fPrimePositive && !fPrimeNegative) {
            f.subSection("Проверка условия сходимости метода простой итерации:")
             .line("f'(x) меняет знак на интервале [a,b]")
             .line("Невозможно гарантировать сходимость метода простой итерации")
             .blank();
            return false;
        }

        String lambdaSign;
        double lambda;
        if (fPrimePositive) {
            lambda = -1.0 / maxAbsDf;
            lambdaSign = "f'(x) > 0 на [a,b] → λ = -1/max|f'(x)|";
        } else {
            lambda = 1.0 / maxAbsDf;
            lambdaSign = "f'(x) < 0 на [a,b] → λ = +1/max|f'(x)|";
        }
        f.subSection("Построение итерационной функции φ(x):")
         .line("φ(x) = x + λ·f(x),  φ'(x) = 1 + λ·f'(x)")
         .line("%s", lambdaSign)
         .line("max|f'(x)| на [a,b] ≈ %s", maxAbsDf)
         .line("λ = %s", lambda).blank()
         .subSection("Проверка условия сходимости:")
         .line("Требуется: |φ'(x)| < 1 на интервале [a,b]");
        return true;
    }

    private void updateEquation() {
        int index = equationComboBox.getSelectionModel().getSelectedIndex();
        if (index >= 0 && index < equations.size()) {
            currentEquation = equations.get(index);
            aField.setText(String.valueOf(currentEquation.getDefaultA()));
            bField.setText(String.valueOf(currentEquation.getDefaultB()));
        }
    }

    private void updateChart() {
        if (currentEquation == null) return;
        try {
            double a = GuiUtils.parseDouble(aField.getText());
            double b = GuiUtils.parseDouble(bField.getText());
            if (a >= b) return;
            XYChart chart = ChartExporter.createEquationChart(currentEquation, a, b);
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
                aField.setText(data[0]);
                bField.setText(data[1]);
                epsilonField.setText(data[2]);
                resultArea.setText(ResultFormatter.builder()
                    .line("Данные загружены из файла:")
                    .line("  a = %s", data[0])
                    .line("  b = %s", data[1])
                    .line("  ε = %s", data[2]).toString());
            } catch (Exception e) {
                showError("Ошибка загрузки файла: " + e.getMessage());
            }
        }
    }
}
