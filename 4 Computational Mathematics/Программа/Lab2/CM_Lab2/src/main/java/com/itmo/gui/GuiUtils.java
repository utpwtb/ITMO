package com.itmo.gui;

import com.itmo.io.FileUtils;
import javafx.scene.control.Alert;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.File;
import java.io.IOException;

public final class GuiUtils {
    private GuiUtils() {}

    public static double parseDouble(String input) {
        String normalized = input.replace(',', '.');
        return Double.parseDouble(normalized);
    }

    public static void saveToFile(Stage stage, String content, String defaultFileName) {
        if (content == null || content.isEmpty()) {
            return;
        }

        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Сохранить результат");
        fileChooser.setInitialFileName(defaultFileName);
        File file = fileChooser.showSaveDialog(stage);

        if (file != null) {
            try {
                FileUtils.writeContent(file, content);
            } catch (IOException e) {
                Alert alert = new Alert(Alert.AlertType.ERROR);
                alert.setTitle("Ошибка");
                alert.setHeaderText("Ошибка сохранения файла");
                alert.setContentText(e.getMessage());
                alert.initOwner(stage);
                alert.showAndWait();
            }
        }
    }
}
