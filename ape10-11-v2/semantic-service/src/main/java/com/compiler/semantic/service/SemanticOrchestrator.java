package com.compiler.semantic.service;

import com.compiler.semantic.model.CompileResponse;
import com.compiler.semantic.model.CompilerError;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class SemanticOrchestrator {

    private final LexicalServiceClient lexicalClient;
    private final SyntacticServiceClient syntacticClient;
    private final SemanticAnalyzer semanticAnalyzer;
    private final OllamaService ollamaService;

    private final Map<String, LexicalServiceClient.LexicalResult> lexicalCache = new ConcurrentHashMap<>();

    public SemanticOrchestrator(LexicalServiceClient lexicalClient,
                                 SyntacticServiceClient syntacticClient,
                                 SemanticAnalyzer semanticAnalyzer,
                                 OllamaService ollamaService) {
        this.lexicalClient = lexicalClient;
        this.syntacticClient = syntacticClient;
        this.semanticAnalyzer = semanticAnalyzer;
        this.ollamaService = ollamaService;
    }

    public CompileResponse compile(String code) {
        CompileResponse response = new CompileResponse();
        response.setText(code);
        response.setSuccess(false);

        String codeKey = code.trim();

        // Fase 1: Léxico
        LexicalServiceClient.LexicalResult lexResult;
        if (lexicalCache.containsKey(codeKey)) {
            lexResult = lexicalCache.get(codeKey);
        } else {
            lexResult = lexicalClient.tokenize(code);
            lexicalCache.put(codeKey, lexResult);
        }

        response.setTokens(lexResult.tokens);

        if (!lexResult.errors.isEmpty()) {
            response.setErrors(lexResult.errors);
            response.setLlmExplanation(ollamaService.generateGlobalExplanation(code, lexResult.errors));
            response.setErrorExplanations(ollamaService.generateStructuredExplanations(code, lexResult.errors));
            return response;
        }

        // Fase 2: Sintáctico
        SyntacticServiceClient.SyntacticResult synResult = syntacticClient.parse(lexResult.tokens);

        if (!synResult.errors.isEmpty()) {
            response.setErrors(synResult.errors);
            response.setLlmExplanation(ollamaService.generateGlobalExplanation(code, synResult.errors));
            response.setErrorExplanations(ollamaService.generateStructuredExplanations(code, synResult.errors));
            return response;
        }

        response.setTree(synResult.tree);

        // Fase 3: Semántico
        SemanticAnalyzer.AnalysisResult semResult = semanticAnalyzer.analyze(synResult.tree);

        if (!semResult.errors.isEmpty()) {
            response.setErrors(semResult.errors);
            response.setSymbolTable(semResult.symbolTable.show());
            response.setLlmExplanation(ollamaService.generateGlobalExplanation(code, semResult.errors));
            response.setErrorExplanations(ollamaService.generateStructuredExplanations(code, semResult.errors));
            return response;
        }

        response.setSuccess(true);
        response.setSymbolTable(semResult.symbolTable.show());
        response.setLlmExplanation(ollamaService.generateGlobalExplanation(code, null));
        return response;
    }

    public void clearCache() {
        lexicalCache.clear();
    }
}
