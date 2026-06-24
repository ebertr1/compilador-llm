package compiler;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.text.Font;
import javafx.stage.Stage;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class CompilerGUI extends Application {

    private TextArea codeArea;
    private TextArea resultArea;
    private TextArea llmArea;
    private CompilerBackend backend;
    private String projectRoot;

    @Override
    public void start(Stage stage) {
        projectRoot = System.getProperty("user.dir");
        if (projectRoot.endsWith("/frontend-java")) {
            projectRoot = Paths.get(projectRoot).getParent().toString();
        }
        backend = new CompilerBackend(projectRoot);

        stage.setTitle("Compilador - Lenguaje Tipado Estático");

        BorderPane root = new BorderPane();
        root.setPadding(new Insets(10));

        VBox topPanel = new VBox(8);
        Label codeLabel = new Label("Código fuente:");
        codeLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 14px;");

        codeArea = new TextArea();
        codeArea.setFont(Font.font("Monospaced", 14));
        codeArea.setPrefRowCount(12);
        codeArea.setPromptText("Escribe tu código aquí...\nEjemplo:\nint x = 5;\nstring nombre = \"Juan\";\nfloat pi = 3.14;");

        topPanel.getChildren().addAll(codeLabel, codeArea);

        HBox buttonBar = new HBox(10);
        buttonBar.setPadding(new Insets(5, 0, 5, 0));

        Button runBtn = new Button("Ejecutar compilador");
        runBtn.setStyle("-fx-font-size: 14px; -fx-background-color: #4CAF50; -fx-text-fill: white; -fx-padding: 8 16;");

        Button loadCorrectBtn = new Button("Cargar correct.txt");
        Button loadErrorsBtn = new Button("Cargar errors.txt");
        Button clearBtn = new Button("Limpiar");

        buttonBar.getChildren().addAll(runBtn, loadCorrectBtn, loadErrorsBtn, clearBtn);
        topPanel.getChildren().add(buttonBar);
        root.setTop(topPanel);

        TabPane tabPane = new TabPane();

        Tab compilerTab = new Tab("Compilador");
        compilerTab.setClosable(false);
        resultArea = new TextArea();
        resultArea.setEditable(false);
        resultArea.setFont(Font.font("Monospaced", 13));
        resultArea.setWrapText(true);
        compilerTab.setContent(resultArea);

        Tab llmTab = new Tab("Explicación LLM");
        llmTab.setClosable(false);
        llmArea = new TextArea();
        llmArea.setEditable(false);
        llmArea.setFont(Font.font("Monospaced", 13));
        llmArea.setWrapText(true);
        llmTab.setContent(llmArea);

        tabPane.getTabs().addAll(compilerTab, llmTab);

        VBox bottomPanel = new VBox(tabPane);
        bottomPanel.setPrefHeight(300);
        root.setBottom(bottomPanel);

        runBtn.setOnAction(e -> runCompiler());
        loadCorrectBtn.setOnAction(e -> loadExample("examples/correct.txt"));
        loadErrorsBtn.setOnAction(e -> loadExample("examples/errors.txt"));
        clearBtn.setOnAction(e -> {
            codeArea.clear();
            resultArea.clear();
            llmArea.clear();
        });

        Scene scene = new Scene(root, 900, 700);
        stage.setScene(scene);
        stage.show();
    }

    private void runCompiler() {
        String code = codeArea.getText();
        if (code.isBlank()) {
            resultArea.setText("No hay código para compilar.");
            return;
        }

        resultArea.setText("Compilando...\n");
        llmArea.setText("");

        CompilerBackend.CompilerResult result = backend.compile(code);

        if (result.success) {
            resultArea.setStyle("-fx-text-fill: #2e7d32;");
            resultArea.setText(result.compilerOutput);
        } else {
            resultArea.setStyle("-fx-text-fill: #c62828;");
            resultArea.setText("ERRORES DE COMPILACIÓN:\n\n" + result.compilerOutput);
        }

        if (result.llmOutput != null && !result.llmOutput.isEmpty()) {
            llmArea.setText(result.llmOutput);
        } else {
            llmArea.setText("(No hay explicación disponible)");
        }
    }

    private void loadExample(String relativePath) {
        try {
            Path path = Paths.get(projectRoot, relativePath);
            if (Files.exists(path)) {
                String content = Files.readString(path);
                codeArea.setText(content);
            } else {
                resultArea.setText("No se encontró: " + path.toAbsolutePath());
            }
        } catch (IOException e) {
            resultArea.setText("Error al cargar archivo: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
