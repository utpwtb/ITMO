package com.itmo.gui;

import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.HBox;

import java.util.ArrayList;
import java.util.List;

public final class FormBuilder {

    private FormBuilder() {}

    public static RowBuilder row() {
        return new RowBuilder();
    }

    public static class RowBuilder {
        private final List<Node> children = new ArrayList<>();

        public RowBuilder label(String text, Node control) {
            children.add(new Label(text + ":"));
            children.add(control);
            return this;
        }

        public RowBuilder labelValue(String labelText, String value) {
            children.add(new Label(labelText + ":"));
            children.add(new Label(value));
            return this;
        }

        public RowBuilder spacer() {
            javafx.scene.layout.Region spacer = new javafx.scene.layout.Region();
            spacer.setPrefWidth(10);
            children.add(spacer);
            return this;
        }

        public RowBuilder node(Node n) {
            children.add(n);
            return this;
        }

        public HBox build() {
            HBox box = new HBox(10);
            box.setAlignment(Pos.CENTER_LEFT);
            box.getChildren().addAll(children);
            return box;
        }
    }

    public static TextField numberField(String defaultValue) {
        TextField field = new TextField(defaultValue);
        field.setPrefWidth(100);
        return field;
    }

    public static <T> ComboBox<T> comboBox(T... items) {
        ComboBox<T> combo = new ComboBox<>();
        combo.getItems().addAll(items);
        combo.getSelectionModel().selectFirst();
        return combo;
    }

    public static <T> ComboBox<T> comboBox(List<T> items) {
        ComboBox<T> combo = new ComboBox<>();
        combo.getItems().addAll(items);
        combo.getSelectionModel().selectFirst();
        return combo;
    }
}
