package com.compiler.syntactic.model;

import java.util.List;

public class ParseRequest {
    private List<Token> tokens;

    public List<Token> getTokens() { return tokens; }
    public void setTokens(List<Token> tokens) { this.tokens = tokens; }
}
