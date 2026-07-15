package com.compiler.semantic.model;

public class CompilerError {
    private String type;
    private int line;
    private String message;

    public CompilerError() {}

    public CompilerError(String type, int line, String message) {
        this.type = type; this.line = line; this.message = message;
    }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public int getLine() { return line; }
    public void setLine(int line) { this.line = line; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
