package compiler;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class CompilerBackend {

    private final String projectRoot;

    public CompilerBackend(String projectRoot) {
        this.projectRoot = projectRoot;
    }

    public CompilerResult compile(String code) {
        CompilerResult result = new CompilerResult();

        try {
            File tempFile = File.createTempFile("compiler_input_", ".txt");
            tempFile.deleteOnExit();
            Files.writeString(tempFile.toPath(), code);

            ProcessBuilder pb = new ProcessBuilder(
                "python3",
                projectRoot + "/backend/main.py",
                "--json"
            );
            pb.redirectInput(tempFile);
            pb.redirectErrorStream(false);

            Process process = pb.start();
            String output = new String(process.getInputStream().readAllBytes());
            String errorOutput = new String(process.getErrorStream().readAllBytes());
            int exitCode = process.waitFor();

            tempFile.delete();

            if (exitCode != 0 && output.isEmpty()) {
                result.success = false;
                result.errors.add("Error ejecutando el compilador: " + errorOutput);
                return result;
            }

            parseJson(output, result);

        } catch (Exception e) {
            result.success = false;
            result.errors.add("Excepción: " + e.getMessage());
        }

        return result;
    }

    private void parseJson(String json, CompilerResult result) {
        try {
            json = json.trim();

            result.success = json.contains("\"success\": true");

            String[] lines = json.split("\n");

            StringBuilder errorsText = new StringBuilder();
            StringBuilder llmText = new StringBuilder();
            boolean inErrors = false;
            boolean inLlm = false;
            boolean inSymbols = false;
            StringBuilder symbolsText = new StringBuilder();

            for (String line : lines) {
                String trimmed = line.trim();

                if (trimmed.startsWith("\"errors\":")) {
                    inErrors = true;
                    inLlm = false;
                    inSymbols = false;
                    continue;
                }
                if (trimmed.startsWith("\"symbol_table\":")) {
                    inErrors = false;
                    inLlm = false;
                    inSymbols = true;
                    continue;
                }
                if (trimmed.startsWith("\"llm_explanation\":")) {
                    inErrors = false;
                    inLlm = true;
                    inSymbols = false;
                    String value = extractStringValue(trimmed);
                    if (!value.isEmpty()) {
                        llmText.append(value);
                    }
                    continue;
                }
                if (trimmed.startsWith("\"success\":")) {
                    continue;
                }

                if (inErrors) {
                    if (trimmed.contains("\"message\":")) {
                        String msg = extractStringValue(trimmed);
                        if (!msg.isEmpty()) {
                            result.errors.add(msg);
                            errorsText.append("• ").append(msg).append("\n");
                        }
                    }
                }

                if (inLlm) {
                    String value = extractStringValue(trimmed);
                    if (!value.isEmpty()) {
                        if (llmText.length() > 0) llmText.append(" ");
                        llmText.append(value);
                    }
                }

                if (inSymbols) {
                    if (trimmed.contains(":")) {
                        symbolsText.append(trimmed.replaceAll("[{},]", "").replace("\"", "")).append("\n");
                    }
                }
            }

            result.compilerOutput = errorsText.length() > 0
                ? errorsText.toString()
                : "Compilación exitosa.\n\nTabla de símbolos:\n" + symbolsText;

            result.llmOutput = llmText.toString().replaceAll("^\"|\"$", "");

        } catch (Exception e) {
            result.success = false;
            result.errors.add("Error parseando JSON: " + e.getMessage());
            result.compilerOutput = json;
        }
    }

    private String extractStringValue(String line) {
        int colonIdx = line.indexOf(':');
        if (colonIdx < 0) return "";
        String value = line.substring(colonIdx + 1).trim();
        if (value.startsWith("\"") && value.endsWith("\"")) {
            value = value.substring(1, value.length() - 1);
        } else if (value.startsWith("\"")) {
            value = value.substring(1);
        }
        value = value.replace("\\n", "\n");
        return value;
    }

    public static class CompilerResult {
        public boolean success;
        public List<String> errors = new ArrayList<>();
        public String compilerOutput = "";
        public String llmOutput = "";
    }
}
