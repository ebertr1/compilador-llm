package com.compiler.lexical.model;

import java.util.List;

public class LexResponse {
    private List<Token> tokens;
    private List<CompilerError> errors;

    public LexResponse() {}

    public LexResponse(List<Token> tokens, List<CompilerError> errors) {
        this.tokens = tokens;
        this.errors = errors;
    }

    public List<Token> getTokens() { return tokens; }
    public void setTokens(List<Token> tokens) { this.tokens = tokens; }
    public List<CompilerError> getErrors() { return errors; }
    public void setErrors(List<CompilerError> errors) { this.errors = errors; }
}
