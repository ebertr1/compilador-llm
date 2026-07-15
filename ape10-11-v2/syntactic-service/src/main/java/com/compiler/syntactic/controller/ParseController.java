package com.compiler.syntactic.controller;

import com.compiler.syntactic.model.ParseRequest;
import com.compiler.syntactic.model.ParseResponse;
import com.compiler.syntactic.service.ParserService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/parse")
public class ParseController {

    private final ParserService parserService;

    public ParseController(ParserService parserService) {
        this.parserService = parserService;
    }

    @PostMapping
    public ParseResponse parse(@RequestBody ParseRequest request) {
        return parserService.parse(request.getTokens());
    }
}
