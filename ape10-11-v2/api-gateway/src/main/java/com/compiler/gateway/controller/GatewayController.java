package com.compiler.gateway.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.nio.file.Files;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class GatewayController {

    private final RestTemplate restTemplate;
    private final String semanticUrl;

    public GatewayController(RestTemplate restTemplate,
                              @Value("${services.semantic.url}") String semanticUrl) {
        this.restTemplate = restTemplate;
        this.semanticUrl = semanticUrl;
    }

    @PostMapping("/compile")
    public ResponseEntity<Object> compile(@RequestBody Map<String, String> request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        try {
            ResponseEntity<Object> response = restTemplate.exchange(
                semanticUrl + "/compile",
                HttpMethod.POST,
                entity,
                Object.class
            );
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of(
                "success", false,
                "error", "Semantic service unavailable: " + e.getMessage()
            ));
        }
    }

    @GetMapping("/examples/{name}")
    public ResponseEntity<Map<String, String>> getExample(@PathVariable String name) {
        try {
            ClassPathResource resource = new ClassPathResource("examples/" + name);
            if (!resource.exists()) {
                return ResponseEntity.notFound().build();
            }
            String content = Files.readString(resource.getFile().toPath());
            return ResponseEntity.ok(Map.of("code", content));
        } catch (IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "ok"));
    }
}
