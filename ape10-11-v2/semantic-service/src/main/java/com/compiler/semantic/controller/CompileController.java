package com.compiler.semantic.controller;

import com.compiler.semantic.model.CompileRequest;
import com.compiler.semantic.model.CompileResponse;
import com.compiler.semantic.service.SemanticOrchestrator;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/compile")
public class CompileController {

    private final SemanticOrchestrator orchestrator;

    public CompileController(SemanticOrchestrator orchestrator) {
        this.orchestrator = orchestrator;
    }

    @PostMapping
    public CompileResponse compile(@RequestBody CompileRequest request) {
        return orchestrator.compile(request.getCode());
    }
}
