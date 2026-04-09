package com.itmo.gui;

import io.fair_acc.chartfx.XYChart;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import org.controlsfx.control.Notifications;

import java.util.List;

public abstract class BaseSolverView {
    protected Stage stage;
    protected TextArea resultArea;
    protected BorderPane chartContainer;
    private final String windowTitle;
    private final String defaultFileName;
    private Button solveBtn;
    private Button saveBtn;
    private Button backBtn;

    protected BaseSolverView(String windowTitle, String defaultFileName) {
        this.windowTitle = windowTitle;
        this.defaultFileName = defaultFileName;
    }

    public void show(Stage primaryStage) {
        stage = primaryStage;
        stage.setTitle(windowTitle);

        VBox topPanel = buildTopPanel();
        HBox bottomPanel = buildBottomPanel();

        BorderPane root = new BorderPane();
        root.setTop(topPanel);
        root.setCenter(bottomPanel);

        bindEvents();

        Scene scene = new Scene(root, 1100, 800);
        stage.setScene(scene);
        stage.show();

        onShow();
    }

    private VBox buildTopPanel() {
        Label titleLabel = new Label(getTitleText());
        titleLabel.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");

        List<Node> formRows = createFormRows();
        HBox buttonRow = createButtonRow();

        VBox topPanel = new VBox(15);
        topPanel.setPadding(new Insets(15));
        topPanel.getChildren().add(titleLabel);
        topPanel.getChildren().addAll(formRows);
        topPanel.getChildren().add(buttonRow);

        return topPanel;
    }

    private HBox buildBottomPanel() {
        resultArea = new TextArea();
        resultArea.setPrefRowCount(20);
        resultArea.setPrefWidth(500);
        resultArea.setEditable(false);
        resultArea.setWrapText(true);
        resultArea.setStyle("-fx-font-family: monospace; -fx-font-size: 12px;");

        chartContainer = new BorderPane();

        VBox leftPanel = new VBox(10);
        leftPanel.setPadding(new Insets(15));
        leftPanel.setPrefWidth(500);
        leftPanel.getChildren().addAll(new Label("Результат:"), resultArea);
        VBox.setVgrow(resultArea, Priority.ALWAYS);

        VBox rightPanel = new VBox(10);
        rightPanel.setPadding(new Insets(15));
        rightPanel.setPrefWidth(500);
        rightPanel.getChildren().addAll(new Label("График:"), chartContainer);
        VBox.setVgrow(chartContainer, Priority.ALWAYS);

        HBox bottomPanel = new HBox(15);
        bottomPanel.setPadding(new Insets(0, 15, 15, 15));
        bottomPanel.getChildren().addAll(leftPanel, rightPanel);
        HBox.setHgrow(leftPanel, Priority.ALWAYS);
        HBox.setHgrow(rightPanel, Priority.ALWAYS);

        return bottomPanel;
    }

    private HBox createButtonRow() {
        Button[] extraButtons = getExtraButtons();
        solveBtn = createSolveButton();
        saveBtn = createSaveButton();
        backBtn = createBackButton();

        HBox buttonBox = new HBox(10);
        buttonBox.setAlignment(Pos.CENTER);
        for (Button btn : extraButtons) {
            buttonBox.getChildren().add(btn);
        }
        buttonBox.getChildren().addAll(solveBtn, saveBtn, backBtn);
        return buttonBox;
    }

    private void bindEvents() {
        solveBtn.setOnAction(e -> solve());
        saveBtn.setOnAction(e -> saveResult());
        backBtn.setOnAction(e -> goBack());
    }

    private static Button createSolveButton() {
        Button btn = new Button("Решить");
        btn.setPrefWidth(150);
        btn.setStyle("-fx-background-color: #4CAF50; -fx-text-fill: white;");
        return btn;
    }

    private static Button createSaveButton() {
        Button btn = new Button("Сохранить результат");
        btn.setPrefWidth(150);
        return btn;
    }

    private static Button createBackButton() {
        Button btn = new Button("Назад");
        btn.setPrefWidth(150);
        return btn;
    }

    protected void goBack() {
        MainWindow main = new MainWindow();
        main.start(stage);
    }

    protected void saveResult() {
        String content = resultArea.getText();
        if (content == null || content.isEmpty()) {
            showError("Нет результатов для сохранения.");
            return;
        }
        GuiUtils.saveToFile(stage, content, defaultFileName);
    }

    protected void updateChart(XYChart chart) {
        chartContainer.setCenter(chart);
    }

    protected void showError(String message) {
        Notifications.create()
                .title("Ошибка")
                .text(message)
                .owner(stage)
                .showError();
    }

    protected void showInfo(String message) {
        Notifications.create()
                .title("Информация")
                .text(message)
                .owner(stage)
                .showInformation();
    }

    protected abstract String getTitleText();
    protected abstract List<Node> createFormRows();
    protected abstract Button[] getExtraButtons();
    protected abstract void onShow();
    protected abstract void solve();
}
