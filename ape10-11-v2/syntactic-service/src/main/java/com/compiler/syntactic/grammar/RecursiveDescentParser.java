package com.compiler.syntactic.grammar;

import com.compiler.syntactic.model.*;
import java.util.*;

public class RecursiveDescentParser {
    private List<Token> tokens;
    private int pos;
    private List<CompilerError> errors;

    public ParseResponse parse(List<Token> tokens) {
        this.tokens = tokens;
        this.pos = 0;
        this.errors = new ArrayList<>();

        AstNode program = parseProgram();

        return new ParseResponse(program, errors);
    }

    private Token peek() {
        return pos < tokens.size() ? tokens.get(pos) : null;
    }

    private Token advance() {
        return tokens.get(pos++);
    }

    private boolean match(String... types) {
        Token t = peek();
        if (t == null) return false;
        for (String type : types) {
            if (t.getType().equals(type)) return true;
        }
        return false;
    }

    private Token expect(String type, String errorMsg) {
        Token t = peek();
        if (t != null && t.getType().equals(type)) {
            return advance();
        }
        int line = t != null ? t.getLine() : 0;
        String val = t != null ? t.getValue() : "EOF";
        errors.add(new CompilerError("syntactic", line,
            errorMsg + " Se encontró '" + val + "'"));
        return null;
    }

    private AstNode parseProgram() {
        AstNode node = new AstNode("Program");
        List<AstNode> stmts = new ArrayList<>();

        while (peek() != null && !peek().getType().equals("RBRACE")) {
            AstNode stmt = parseStatement();
            if (stmt != null) stmts.add(stmt);
            else break;
        }

        node.put("statements", stmts);
        return node;
    }

    private AstNode parseStatement() {
        if (match("ENTERO", "FLOTANTE", "CADENA")) {
            return parseDeclaration();
        }
        if (match("ENETRO")) {
            return parseEnetroDef();
        }
        if (match("SI")) {
            return parseIfStmt();
        }
        if (match("MIENTRAS")) {
            return parseWhileStmt();
        }
        if (match("PARA")) {
            return parseForStmt();
        }
        if (match("IMPRIMIR")) {
            return parsePrintStmt();
        }
        if (match("ID")) {
            return parseAssignmentOrAccess();
        }
        return null;
    }

    private AstNode parseDeclaration() {
        Token typeTok = advance();
        Token idTok = expect("ID", "Se esperaba un identificador");
        if (idTok == null) return null;

        String type = typeTok.getValue().toLowerCase();
        String name = idTok.getValue();
        int line = idTok.getLine();

        if (match("ASSIGN")) {
            advance();
            AstNode expr = parseExpression();
            expect("SEMICOLON", "Falta punto y coma ';'");
            AstNode node = new AstNode("VarDecl");
            node.put("varType", type);
            node.put("name", name);
            node.put("value", expr);
            node.put("line", line);
            return node;
        }

        expect("SEMICOLON", "Falta punto y coma ';'");
        AstNode decl = new AstNode("VarDecl");
        decl.put("varType", type);
        decl.put("name", name);
        decl.put("line", line);
        return decl;
    }

    private AstNode parseAssignmentOrAccess() {
        Token idTok = advance();
        if (match("ASSIGN")) {
            advance();
            AstNode expr = parseExpression();
            expect("SEMICOLON", "Falta punto y coma ';'");
            AstNode node = new AstNode("Assign");
            node.put("name", idTok.getValue());
            node.put("value", expr);
            node.put("line", idTok.getLine());
            return node;
        }
        if (match("DOT")) {
            advance();
            Token fieldTok = expect("ID", "Se esperaba nombre de campo");
            if (fieldTok == null) return null;
            expect("SEMICOLON", "Falta punto y coma ';'");
            AstNode node = new AstNode("EnetroAccess");
            node.put("enetroName", idTok.getValue());
            node.put("fieldName", fieldTok.getValue());
            node.put("line", idTok.getLine());
            return node;
        }
        errors.add(new CompilerError("syntactic", idTok.getLine(),
            "Se esperaba '=' o '.' después de '" + idTok.getValue() + "'"));
        return null;
    }

    private AstNode parseExpression() {
        return parseComparison();
    }

    private AstNode parseComparison() {
        AstNode left = parseAdditive();
        while (match("EQ", "NE", "LT", "GT", "LE", "GE")) {
            Token op = advance();
            AstNode right = parseAdditive();
            AstNode binOp = new AstNode("BinOp");
            binOp.put("left", left);
            binOp.put("op", op.getValue());
            binOp.put("right", right);
            binOp.put("line", op.getLine());
            left = binOp;
        }
        return left;
    }

    private AstNode parseAdditive() {
        AstNode left = parseMultiplicative();
        while (match("PLUS", "MINUS")) {
            Token op = advance();
            AstNode right = parseMultiplicative();
            AstNode binOp = new AstNode("BinOp");
            binOp.put("left", left);
            binOp.put("op", op.getValue());
            binOp.put("right", right);
            binOp.put("line", op.getLine());
            left = binOp;
        }
        return left;
    }

    private AstNode parseMultiplicative() {
        AstNode left = parseUnary();
        while (match("TIMES", "DIVIDE", "MOD")) {
            Token op = advance();
            AstNode right = parseUnary();
            AstNode binOp = new AstNode("BinOp");
            binOp.put("left", left);
            binOp.put("op", op.getValue());
            binOp.put("right", right);
            binOp.put("line", op.getLine());
            left = binOp;
        }
        return left;
    }

    private AstNode parseUnary() {
        if (match("MINUS")) {
            Token op = advance();
            AstNode operand = parseUnary();
            AstNode node = new AstNode("UnaryOp");
            node.put("op", op.getValue());
            node.put("operand", operand);
            node.put("line", op.getLine());
            return node;
        }
        return parsePrimary();
    }

    private AstNode parsePrimary() {
        if (match("NUMBER")) {
            Token t = advance();
            AstNode node = new AstNode("Literal");
            node.put("value", t.getValue());
            node.put("literalType", "entero");
            node.put("line", t.getLine());
            return node;
        }
        if (match("FLOAT_NUMBER")) {
            Token t = advance();
            AstNode node = new AstNode("Literal");
            node.put("value", t.getValue());
            node.put("literalType", "flotante");
            node.put("line", t.getLine());
            return node;
        }
        if (match("TEXT")) {
            Token t = advance();
            AstNode node = new AstNode("Literal");
            node.put("value", t.getValue());
            node.put("literalType", "cadena");
            node.put("line", t.getLine());
            return node;
        }
        if (match("ID")) {
            Token t = advance();
            if (match("DOT")) {
                advance();
                Token field = expect("ID", "Se esperaba nombre de campo");
                if (field == null) return null;
                AstNode node = new AstNode("EnetroAccess");
                node.put("enetroName", t.getValue());
                node.put("fieldName", field.getValue());
                node.put("line", t.getLine());
                return node;
            }
            AstNode node = new AstNode("VarRef");
            node.put("name", t.getValue());
            node.put("line", t.getLine());
            return node;
        }
        if (match("LPAREN")) {
            advance();
            AstNode expr = parseExpression();
            expect("RPAREN", "Falta paréntesis ')'");
            return expr;
        }
        errors.add(new CompilerError("syntactic",
            peek() != null ? peek().getLine() : 0,
            "Expresión inesperada"));
        return null;
    }

    private AstNode parseIfStmt() {
        Token ifTok = advance();
        expect("LPAREN", "Falta '(' después de 'si'");
        AstNode cond = parseExpression();
        expect("RPAREN", "Falta ')'");
        AstNode thenBlock = parseBlock();

        AstNode elseBlock = null;
        if (match("SINO")) {
            advance();
            elseBlock = parseBlock();
        }

        AstNode node = new AstNode("IfStmt");
        node.put("condition", cond);
        node.put("thenBlock", thenBlock);
        node.put("elseBlock", elseBlock);
        node.put("line", ifTok.getLine());
        return node;
    }

    private AstNode parseWhileStmt() {
        Token whileTok = advance();
        expect("LPAREN", "Falta '(' después de 'mientras'");
        AstNode cond = parseExpression();
        expect("RPAREN", "Falta ')'");
        AstNode body = parseBlock();

        AstNode node = new AstNode("WhileStmt");
        node.put("condition", cond);
        node.put("body", body);
        node.put("line", whileTok.getLine());
        return node;
    }

    private AstNode parseForStmt() {
        Token forTok = advance();
        expect("LPAREN", "Falta '(' después de 'para'");

        Token idInit = expect("ID", "Se esperaba variable en inicialización");
        expect("ASSIGN", "Se esperaba '='");
        AstNode initExpr = parseExpression();
        AstNode init = new AstNode("Assign");
        if (idInit != null) {
            init.put("name", idInit.getValue());
            init.put("line", idInit.getLine());
        }
        init.put("value", initExpr);

        expect("SEMICOLON", "Falta ';' en condición del 'para'");

        AstNode cond = parseExpression();
        expect("SEMICOLON", "Falta ';' en actualización del 'para'");

        Token idUpd = expect("ID", "Se esperaba variable en actualización");
        expect("ASSIGN", "Se esperaba '='");
        AstNode updExpr = parseExpression();
        AstNode update = new AstNode("Assign");
        if (idUpd != null) {
            update.put("name", idUpd.getValue());
            update.put("line", idUpd.getLine());
        }
        update.put("value", updExpr);

        expect("RPAREN", "Falta ')'");

        AstNode body = parseBlock();

        AstNode node = new AstNode("ForStmt");
        node.put("init", init);
        node.put("condition", cond);
        node.put("update", update);
        node.put("body", body);
        node.put("line", forTok.getLine());
        return node;
    }

    private AstNode parsePrintStmt() {
        Token printTok = advance();
        expect("LPAREN", "Falta '(' después de 'imprimir'");
        AstNode expr = parseExpression();
        expect("RPAREN", "Falta ')'");
        expect("SEMICOLON", "Falta ';'");

        AstNode node = new AstNode("PrintStmt");
        node.put("expression", expr);
        node.put("line", printTok.getLine());
        return node;
    }

    private AstNode parseEnetroDef() {
        Token enetroTok = advance();
        Token idTok = expect("ID", "Se esperaba nombre del ENETRO");
        expect("LBRACE", "Falta '{'");

        List<AstNode> fields = new ArrayList<>();
        while (peek() != null && !peek().getType().equals("RBRACE")) {
            if (match("ENTERO", "FLOTANTE", "CADENA")) {
                AstNode field = parseEnetroField();
                if (field != null) fields.add(field);
            } else break;
        }
        expect("RBRACE", "Falta '}'");

        AstNode node = new AstNode("EnetroDef");
        if (idTok != null) {
            node.put("name", idTok.getValue());
            node.put("line", idTok.getLine());
        }
        node.put("fields", fields);
        node.put("line", enetroTok.getLine());
        return node;
    }

    private AstNode parseEnetroField() {
        Token typeTok = advance();
        Token idTok = expect("ID", "Se esperaba nombre de columna");
        if (idTok == null) return null;

        AstNode node = new AstNode("EnetroField");
        node.put("varType", typeTok.getValue().toLowerCase());
        node.put("name", idTok.getValue());
        node.put("line", idTok.getLine());

        if (match("ASSIGN")) {
            advance();
            node.put("value", parseExpression());
        }
        expect("SEMICOLON", "Falta ';'");
        return node;
    }

    private AstNode parseBlock() {
        if (match("LBRACE")) {
            advance();
            AstNode program = parseProgram();
            expect("RBRACE", "Falta '}'");
            AstNode block = new AstNode("Block");
            if (program != null) {
                @SuppressWarnings("unchecked")
                List<AstNode> stmts = (List<AstNode>) program.get("statements");
                block.put("statements", stmts != null ? stmts : new ArrayList<>());
            }
            return block;
        }
        AstNode stmt = parseStatement();
        AstNode block = new AstNode("Block");
        List<AstNode> stmts = new ArrayList<>();
        if (stmt != null) stmts.add(stmt);
        block.put("statements", stmts);
        return block;
    }
}
