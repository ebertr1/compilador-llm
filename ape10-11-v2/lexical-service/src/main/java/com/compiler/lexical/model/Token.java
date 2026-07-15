package com.compiler.lexical.model;

public class Token {
    private String type;
    private String value;
    private int line;

    public Token() {}

    public Token(String type, String value, int line) {
        this.type = type;
        this.value = value;
        this.line = line;
    }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }
    public int getLine() { return line; }
    public void setLine(int line) { this.line = line; }
}
