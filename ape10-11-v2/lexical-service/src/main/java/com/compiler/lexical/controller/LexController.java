package com.compiler.lexical.controller;

import com.compiler.lexical.model.LexRequest;
import com.compiler.lexical.model.LexResponse;
import com.compiler.lexical.service.LexerService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/lex")
public class LexController {

    private final LexerService lexerService;

    public LexController(LexerService lexerService) {
        this.lexerService = lexerService;
    }

    @PostMapping
    public LexResponse lex(@RequestBody LexRequest request) {
        return lexerService.tokenize(request.getCode());
    }
}
