package com.compiler.semantic.service;

import com.compiler.semantic.model.CompilerError;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.regex.*;

@Service
public class OllamaService {

    private static final Logger log = LoggerFactory.getLogger(OllamaService.class);

    private final RestTemplate restTemplate;
    private final String ollamaUrl;
    private final String model;

    public OllamaService(RestTemplate restTemplate,
                         @Value("${ollama.url:http://localhost:11434}") String ollamaUrl,
                         @Value("${ollama.model:gemma3:1b}") String model) {
        this.restTemplate = restTemplate;
        this.ollamaUrl = ollamaUrl;
        this.model = model;
    }

    @PostConstruct
    public void warmUp() {
        try {
            log.info("Warming up OLLAMA model {}...", model);
            String resp = callOllama("Responde solo OK");
            log.info("OLLAMA warm-up complete: {}", resp);
        } catch (Exception e) {
            log.warn("OLLAMA warm-up failed: {}", e.getMessage());
        }
    }

    public String generateGlobalExplanation(String code, List<CompilerError> errors) {
        try {
            return callOllama(buildGlobalPrompt(code, errors));
        } catch (Exception e) {
            log.warn("OLLAMA global request failed: {}", e.getMessage());
            return fallbackGlobal(errors);
        }
    }

    public List<String> generateStructuredExplanations(String code, List<CompilerError> errors) {
        try {
            String raw = callOllama(buildStructuredPrompt(code, errors));
            return parseStructuredResponse(raw, errors.size());
        } catch (Exception e) {
            log.warn("OLLAMA structured request failed: {}", e.getMessage());
            return fallbackStructured(errors);
        }
    }

    private String callOllama(String prompt) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> body = new HashMap<>();
        body.put("model", model);
        body.put("prompt", prompt);
        body.put("stream", false);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            ollamaUrl + "/api/generate",
            HttpMethod.POST,
            entity,
            new ParameterizedTypeReference<>() {}
        );

        Map<String, Object> respBody = response.getBody();
        if (respBody != null && respBody.containsKey("response")) {
            return ((String) respBody.get("response")).trim();
        }
        return null;
    }

    private String buildGlobalPrompt(String code, List<CompilerError> errors) {
        if (errors == null || errors.isEmpty()) {
            return """
                Eres un ingeniero de compiladores. Lenguaje APE10-11
                (keywords español, tipado estático, entero flotante cadena ENETRO).

                Código:
                ```
                %s
                ```

                Compilación exitosa. Explica qué hace este código en 2-3 líneas.
                """.formatted(code).trim();
        }

        StringBuilder sb = new StringBuilder();
        sb.append("""
            Eres un ingeniero de compiladores. Lenguaje APE10-11.
            Código:
            ```
            %s
            ```
            Errores:
            """.formatted(code).trim());

        for (int i = 0; i < errors.size(); i++) {
            CompilerError e = errors.get(i);
            sb.append(i + 1).append(". [").append(tipoLabel(e)).append("] ")
              .append("Línea ").append(e.getLine()).append(": ")
              .append(e.getMessage()).append("\n");
        }

        sb.append("""
            Da un resumen general de los errores encontrados y su impacto.
            Máximo 4 líneas.
            """);
        return sb.toString().trim();
    }

    private String buildStructuredPrompt(String code, List<CompilerError> errors) {
        StringBuilder sb = new StringBuilder();
        sb.append("""
            Eres un ingeniero de compiladores depurando código APE10-11
            (keywords español, tipado estático, tipos: entero flotante cadena ENETRO).

            Código fuente:
            ```
            %s
            ```

            Errores de compilación:
            """.formatted(code).trim());

        for (int i = 0; i < errors.size(); i++) {
            CompilerError e = errors.get(i);
            sb.append("\n--- Error ").append(i + 1).append(" ---\n");
            sb.append("Tipo: [").append(tipoLabel(e)).append("]\n");
            sb.append("Línea: ").append(e.getLine()).append("\n");
            sb.append("Mensaje: ").append(e.getMessage()).append("\n");
        }

        sb.append("""

            Para CADA error, responde en este formato EXACTO (sin desviarte):

            [Error N]
            EXPLICACIÓN TÉCNICA: <análisis de ingeniero: qué regla se violó, por qué el compilador lo rechaza>
            SOLUCIÓN: <código corregido o instrucción precisa>

            No agregues texto adicional fuera de este formato.
            """);
        return sb.toString().trim();
    }

    private List<String> parseStructuredResponse(String raw, int expectedCount) {
        List<String> result = new ArrayList<>();
        if (raw == null || raw.isBlank()) return fallbackStructured(expectedCount);

        // Split by [Error N] markers
        String[] blocks = raw.split("(?=\\[Error \\d+\\])");
        int blockIdx = 0;

        for (String block : blocks) {
            if (block.isBlank()) continue;
            blockIdx++;

            String tech = extractField(block, "EXPLICACIÓN TÉCNICA:");
            String sol = extractField(block, "SOLUCIÓN:");

            if (tech == null && sol == null) continue;

            StringBuilder entry = new StringBuilder();
            if (tech != null) entry.append("EXPLICACIÓN TÉCNICA: ").append(tech.trim());
            if (sol != null) {
                if (!entry.isEmpty()) entry.append("\n");
                entry.append("SOLUCIÓN: ").append(sol.trim());
            }
            result.add(entry.toString());
        }

        // Fill remaining with fallback
        while (result.size() < expectedCount) {
            result.add("EXPLICACIÓN TÉCNICA: Error de compilación detectado.\nSOLUCIÓN: Revisa la línea señalada.");
        }

        return result;
    }

    private String extractField(String block, String fieldName) {
        Pattern p = Pattern.compile(Pattern.quote(fieldName) + "\\s*(.*?)(?=(?:\\n\\[Error \\d+\\]|\\nEXPLICACIÓN TÉCNICA:|\\nSOLUCIÓN:|\\z))", Pattern.DOTALL);
        Matcher m = p.matcher(block);
        if (m.find()) {
            String val = m.group(1).trim();
            return val.isEmpty() ? null : val;
        }
        return null;
    }

    private String tipoLabel(CompilerError e) {
        return switch (e.getType().toLowerCase()) {
            case "lexical" -> "LÉXICO";
            case "syntactic" -> "SINTÁCTICO";
            case "semantic" -> "SEMÁNTICO";
            default -> e.getType().toUpperCase();
        };
    }

    private String fallbackGlobal(List<CompilerError> errors) {
        if (errors == null || errors.isEmpty())
            return "Compilación exitosa.";
        return "Se encontraron " + errors.size() + " error(es) de compilación.";
    }

    private List<String> fallbackStructured(List<CompilerError> errors) {
        return errors.stream().map(e ->
            "EXPLICACIÓN TÉCNICA: Error " + tipoLabel(e) + " en línea " + e.getLine() + ": " + e.getMessage() + "\n" +
            "SOLUCIÓN: Revisa la sintaxis y tipos en la línea " + e.getLine() + "."
        ).toList();
    }

    private List<String> fallbackStructured(int count) {
        List<String> list = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            list.add("EXPLICACIÓN TÉCNICA: Error detectado durante la compilación.\nSOLUCIÓN: Revisa el código fuente.");
        }
        return list;
    }
}
