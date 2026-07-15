package com.compiler.semantic.model;

import java.util.*;

public class CompileResponse {
    private boolean success;
    private List<CompilerError> errors;
    private List<String> errorExplanations;
    private String text;
    private List<Map<String, Object>> tokens;
    private Map<String, Object> tree;
    private Map<String, String> symbolTable;
    private String llmExplanation;

    public CompileResponse() {
        this.errors = new ArrayList<>();
        this.errorExplanations = new ArrayList<>();
        this.tokens = new ArrayList<>();
        this.symbolTable = new HashMap<>();
    }

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public List<CompilerError> getErrors() { return errors; }
    public void setErrors(List<CompilerError> errors) { this.errors = errors; }
    public List<String> getErrorExplanations() { return errorExplanations; }
    public void setErrorExplanations(List<String> errorExplanations) { this.errorExplanations = errorExplanations; }
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
    public List<Map<String, Object>> getTokens() { return tokens; }
    public void setTokens(List<Map<String, Object>> tokens) { this.tokens = tokens; }
    public Map<String, Object> getTree() { return tree; }
    public void setTree(Map<String, Object> tree) { this.tree = tree; }
    public Map<String, String> getSymbolTable() { return symbolTable; }
    public void setSymbolTable(Map<String, String> symbolTable) { this.symbolTable = symbolTable; }
    public String getLlmExplanation() { return llmExplanation; }
    public void setLlmExplanation(String llmExplanation) { this.llmExplanation = llmExplanation; }
}
