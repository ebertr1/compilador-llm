package com.compiler.syntactic.model;

import java.util.List;

public class ParseResponse {
    private AstNode tree;
    private List<CompilerError> errors;

    public ParseResponse() {}

    public ParseResponse(AstNode tree, List<CompilerError> errors) {
        this.tree = tree;
        this.errors = errors;
    }

    public AstNode getTree() { return tree; }
    public void setTree(AstNode tree) { this.tree = tree; }
    public List<CompilerError> getErrors() { return errors; }
    public void setErrors(List<CompilerError> errors) { this.errors = errors; }
}
