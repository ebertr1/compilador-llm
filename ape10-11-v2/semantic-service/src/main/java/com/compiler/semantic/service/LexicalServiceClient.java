package com.compiler.semantic.service;

import com.compiler.semantic.model.CompilerError;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class LexicalServiceClient {

    private final RestTemplate restTemplate;
    private final String lexicalUrl;

    public LexicalServiceClient(RestTemplate restTemplate,
                                 @Value("${services.lexical.url}") String lexicalUrl) {
        this.restTemplate = restTemplate;
        this.lexicalUrl = lexicalUrl;
    }

    public LexicalResult tokenize(String code) {
        Map<String, String> request = Map.of("code", code);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            lexicalUrl + "/lex",
            HttpMethod.POST,
            entity,
            new ParameterizedTypeReference<>() {}
        );

        Map<String, Object> body = response.getBody();
        LexicalResult result = new LexicalResult();

        if (body != null) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> rawTokens = (List<Map<String, Object>>) body.get("tokens");
            result.tokens = rawTokens != null ? rawTokens : new ArrayList<>();

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> rawErrors = (List<Map<String, Object>>) body.get("errors");
            if (rawErrors != null) {
                for (Map<String, Object> e : rawErrors) {
                    result.errors.add(new CompilerError(
                        (String) e.get("type"),
                        e.get("line") instanceof Number ? ((Number) e.get("line")).intValue() : 0,
                        (String) e.get("message")
                    ));
                }
            }
        }
        return result;
    }

    public static class LexicalResult {
        public List<Map<String, Object>> tokens = new ArrayList<>();
        public List<CompilerError> errors = new ArrayList<>();
    }
}
