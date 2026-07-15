package com.compiler.lexical.service;

import com.compiler.lexical.model.*;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class LexerService {

    private static final Set<String> RESERVED = Set.of(
        "entero", "flotante", "cadena", "si", "sino",
        "mientras", "para", "imprimir", "ENETRO"
    );

    private static final Map<String, String> RESERVED_MAP = new HashMap<>();
    static {
        RESERVED_MAP.put("entero", "ENTERO");
        RESERVED_MAP.put("flotante", "FLOTANTE");
        RESERVED_MAP.put("cadena", "CADENA");
        RESERVED_MAP.put("si", "SI");
        RESERVED_MAP.put("sino", "SINO");
        RESERVED_MAP.put("mientras", "MIENTRAS");
        RESERVED_MAP.put("para", "PARA");
        RESERVED_MAP.put("imprimir", "IMPRIMIR");
        RESERVED_MAP.put("ENETRO", "ENETRO");
    }

    public LexResponse tokenize(String code) {
        List<Token> tokens = new ArrayList<>();
        List<CompilerError> errors = new ArrayList<>();
        int line = 1;
        int i = 0;

        while (i < code.length()) {
            char c = code.charAt(i);

            if (c == '\n') { line++; i++; continue; }
            if (c == ' ' || c == '\t' || c == '\r') { i++; continue; }

            if (c == '#') {
                while (i < code.length() && code.charAt(i) != '\n') i++;
                continue;
            }
            if (c == '/' && i + 1 < code.length() && code.charAt(i + 1) == '/') {
                while (i < code.length() && code.charAt(i) != '\n') i++;
                continue;
            }

            if (c == '"') {
                int start = i;
                i++;
                while (i < code.length() && code.charAt(i) != '"') {
                    i++;
                }
                if (i < code.length()) {
                    tokens.add(new Token("TEXT", code.substring(start + 1, i), line));
                    i++;
                } else {
                    errors.add(new CompilerError("lexical", line, start, "Cadena sin cerrar"));
                }
                continue;
            }

            if (Character.isDigit(c)) {
                int start = i;
                boolean isFloat = false;
                while (i < code.length() && Character.isDigit(code.charAt(i))) i++;
                if (i < code.length() && code.charAt(i) == '.') {
                    isFloat = true;
                    i++;
                    while (i < code.length() && Character.isDigit(code.charAt(i))) i++;
                }
                String num = code.substring(start, i);
                tokens.add(new Token(isFloat ? "FLOAT_NUMBER" : "NUMBER", num, line));
                continue;
            }

            if (Character.isLetter(c) || c == '_') {
                int start = i;
                while (i < code.length() && (Character.isLetterOrDigit(code.charAt(i)) || code.charAt(i) == '_')) i++;
                String word = code.substring(start, i);
                String type = RESERVED_MAP.getOrDefault(word, "ID");
                tokens.add(new Token(type, word, line));
                continue;
            }

            String op = handleOperator(code, i, line, tokens, errors);
            if (op != null) {
                i += op.length();
                continue;
            }

            if (c == '{' || c == '}' || c == '(' || c == ')' || c == ';' ||
                c == ',' || c == '.' || c == '+' || c == '-' || c == '*' ||
                c == '/' || c == '%' || c == '=') {
                String sym = String.valueOf(c);
                tokens.add(new Token(symbolToTokenType(sym), sym, line));
                i++;
                continue;
            }

            errors.add(new CompilerError("lexical", line, i, "Caracter desconocido: '" + c + "'"));
            i++;
        }

        return new LexResponse(tokens, errors);
    }

    private String handleOperator(String code, int i, int line, List<Token> tokens, List<CompilerError> errors) {
        if (i + 1 < code.length()) {
            String two = code.substring(i, i + 2);
            switch (two) {
                case "==": tokens.add(new Token("EQ", "==", line)); return two;
                case "!=": tokens.add(new Token("NE", "!=", line)); return two;
                case "<=": tokens.add(new Token("LE", "<=", line)); return two;
                case ">=": tokens.add(new Token("GE", ">=", line)); return two;
            }
        }
        if (i < code.length()) {
            String one = String.valueOf(code.charAt(i));
            switch (one) {
                case "<": tokens.add(new Token("LT", "<", line)); return one;
                case ">": tokens.add(new Token("GT", ">", line)); return one;
                case "=": tokens.add(new Token("ASSIGN", "=", line)); return one;
            }
        }
        return null;
    }

    private String symbolToTokenType(String s) {
        return switch (s) {
            case "+" -> "PLUS";
            case "-" -> "MINUS";
            case "*" -> "TIMES";
            case "/" -> "DIVIDE";
            case "%" -> "MOD";
            case "(" -> "LPAREN";
            case ")" -> "RPAREN";
            case "{" -> "LBRACE";
            case "}" -> "RBRACE";
            case ";" -> "SEMICOLON";
            case "," -> "COMMA";
            case "." -> "DOT";
            case "=" -> "ASSIGN";
            default -> "UNKNOWN";
        };
    }
}
