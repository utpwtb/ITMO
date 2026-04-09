package com.itmo.gui;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.stage.Stage;

public class MainWindow extends Application {
    
    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Решение нелинейных уравнений и систем уравнений");
        
        Label titleLabel = new Label("Решение нелинейных уравнений");
        titleLabel.setFont(Font.font("Arial", FontWeight.BOLD, 20));
        
        Label subtitleLabel = new Label("и систем уравнений");
        subtitleLabel.setFont(Font.font("Arial", FontWeight.BOLD, 20));
        
        Button equationButton = new Button("Решение нелинейного уравнения");
        equationButton.setPrefWidth(300);
        equationButton.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");
        
        Button systemButton = new Button("Решение системы нелинейных уравнений");
        systemButton.setPrefWidth(300);
        systemButton.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");
        
        Button exitButton = new Button("Выход");
        exitButton.setPrefWidth(300);
        exitButton.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");
        
        equationButton.setOnAction(e -> {
            EquationSolverView equationView = new EquationSolverView();
            equationView.show(primaryStage);
        });
        
        systemButton.setOnAction(e -> {
            SystemSolverView systemView = new SystemSolverView();
            systemView.show(primaryStage);
        });
        
        exitButton.setOnAction(e -> primaryStage.close());
        
        VBox root = new VBox(20);
        root.setAlignment(Pos.CENTER);
        root.setPadding(new Insets(40));
        root.getChildren().addAll(titleLabel, subtitleLabel, equationButton, systemButton, exitButton);
        
        Scene scene = new Scene(root, 500, 400);
        primaryStage.setScene(scene);
        primaryStage.show();
    }
    
    public static void launchGUI(String[] args) {
        launch(args);
    }
}
