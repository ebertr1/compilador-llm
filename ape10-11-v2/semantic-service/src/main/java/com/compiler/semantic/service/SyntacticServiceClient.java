package com.compiler.semantic.service;

import com.compiler.semantic.model.CompilerError;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class SyntacticServiceClient {

    private final RestTemplate restTemplate;
    private final String syntacticUrl;

    public SyntacticServiceClient(RestTemplate restTemplate,
                                   @Value("${services.syntactic.url}") String syntacticUrl) {
        this.restTemplate = restTemplate;
        this.syntacticUrl = syntacticUrl;
    }

    public SyntacticResult parse(List<Map<String, Object>> tokens) {
        Map<String, Object> request = Map.of("tokens", tokens);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            syntacticUrl + "/parse",
            HttpMethod.POST,
            entity,
            new ParameterizedTypeReference<>() {}
        );

        Map<String, Object> body = response.getBody();
        SyntacticResult result = new SyntacticResult();

        if (body != null) {
            @SuppressWarnings("unchecked")
            Map<String, Object> rawTree = (Map<String, Object>) body.get("tree");
            result.tree = rawTree;

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

    public static class SyntacticResult {
        public Map<String, Object> tree;
        public List<CompilerError> errors = new ArrayList<>();
    }
}
