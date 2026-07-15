package com.compiler.semantic.controller;

import com.compiler.semantic.model.CompileResponse;
import com.compiler.semantic.service.SemanticOrchestrator;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.*;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.Map;
import java.util.concurrent.*;

@Component
public class CompileWebSocketHandler extends TextWebSocketHandler {

    private final SemanticOrchestrator orchestrator;
    private final ObjectMapper mapper;
    private final ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

    public CompileWebSocketHandler(SemanticOrchestrator orchestrator, ObjectMapper mapper) {
        this.orchestrator = orchestrator;
        this.mapper = mapper;
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();
        @SuppressWarnings("unchecked")
        Map<String, String> data = mapper.readValue(payload, Map.class);
        String code = data.get("code");

        if (code == null) {
            session.sendMessage(new TextMessage("{\"error\":\"Campo 'code' requerido\"}"));
            return;
        }

        executor.submit(() -> {
            try {
                session.sendMessage(new TextMessage("{\"phase\":\"lexical\",\"status\":\"started\"}"));

                CompileResponse response = orchestrator.compile(code);

                session.sendMessage(new TextMessage("{\"phase\":\"lexical\",\"status\":\"done\"}"));
                session.sendMessage(new TextMessage("{\"phase\":\"syntactic\",\"status\":\"done\"}"));
                session.sendMessage(new TextMessage("{\"phase\":\"semantic\",\"status\":\"done\"}"));

                String json = mapper.writeValueAsString(response);
                session.sendMessage(new TextMessage(
                    "{\"type\":\"result\",\"data\":" + json + "}"
                ));
                session.close();
            } catch (Exception e) {
                try {
                    session.sendMessage(new TextMessage(
                        "{\"type\":\"error\",\"message\":\"" + e.getMessage() + "\"}"
                    ));
                } catch (Exception ignored) {}
            }
        });
    }
}
