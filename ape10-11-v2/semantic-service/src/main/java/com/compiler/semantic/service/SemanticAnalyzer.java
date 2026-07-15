package com.compiler.semantic.service;

import com.compiler.semantic.model.CompilerError;
import com.compiler.semantic.model.SymbolTable;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class SemanticAnalyzer {

    private static final Set<String> NUMERIC_TYPES = Set.of("entero", "flotante");
    private static final Set<String> COMPARISON_OPS = Set.of("==", "!=", "<", ">", "<=", ">=");
    private static final Set<String> ARITHMETIC_OPS = Set.of("+", "-", "*", "/");

    public AnalysisResult analyze(Map<String, Object> ast) {
        SymbolTable symbols = new SymbolTable();
        List<CompilerError> errors = new ArrayList<>();
        analyzeNode(ast, symbols, errors);
        return new AnalysisResult(symbols, errors);
    }

    @SuppressWarnings("unchecked")
    private void analyzeNode(Map<String, Object> node, SymbolTable symbols, List<CompilerError> errors) {
        if (node == null) return;
        String type = (String) node.get("type");
        if (type == null) return;

        switch (type) {
            case "Program" -> {
                List<Map<String, Object>> stmts = (List<Map<String, Object>>) node.get("statements");
                if (stmts != null) stmts.forEach(s -> analyzeNode(s, symbols, errors));
            }
            case "VarDecl" -> {
                String name = (String) node.get("name");
                String varType = (String) node.get("varType");
                int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

                if (symbols.existsVariable(name)) {
                    errors.add(new CompilerError("semantic", line,
                        "Variable '" + name + "' ya declarada"));
                    return;
                }

                Map<String, Object> value = (Map<String, Object>) node.get("value");
                if (value != null) {
                    String exprType = resolveType(value, symbols, errors);
                    if (exprType != null && !exprType.equals(varType)) {
                        errors.add(new CompilerError("semantic", line,
                            "Tipo incompatible: se esperaba '" + varType + "' pero se recibió '" + exprType + "'"));
                        return;
                    }
                }
                symbols.addVariable(name, varType);
            }
            case "Assign" -> {
                String name = (String) node.get("name");
                int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

                if (!symbols.existsVariable(name)) {
                    errors.add(new CompilerError("semantic", line,
                        "Variable '" + name + "' no declarada"));
                    return;
                }

                String varType = symbols.getVariableType(name);
                Map<String, Object> value = (Map<String, Object>) node.get("value");
                if (value != null) {
                    String exprType = resolveType(value, symbols, errors);
                    if (exprType != null && !exprType.equals(varType)) {
                        errors.add(new CompilerError("semantic", line,
                            "Tipo incompatible en asignación a '" + name + "'"));
                    }
                }
            }
            case "IfStmt" -> {
                int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;
                Map<String, Object> cond = (Map<String, Object>) node.get("condition");
                String condType = resolveType(cond, symbols, errors);
                if (condType != null && !"entero".equals(condType)) {
                    errors.add(new CompilerError("semantic", line,
                        "La condición del 'si' debe ser 'entero', no '" + condType + "'"));
                }
                analyzeNode((Map<String, Object>) node.get("thenBlock"), symbols, errors);
                analyzeNode((Map<String, Object>) node.get("elseBlock"), symbols, errors);
            }
            case "WhileStmt" -> {
                int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;
                Map<String, Object> cond = (Map<String, Object>) node.get("condition");
                String condType = resolveType(cond, symbols, errors);
                if (condType != null && !"entero".equals(condType)) {
                    errors.add(new CompilerError("semantic", line,
                        "La condición del 'mientras' debe ser 'entero'"));
                }
                analyzeNode((Map<String, Object>) node.get("body"), symbols, errors);
            }
            case "ForStmt" -> {
                Map<String, Object> init = (Map<String, Object>) node.get("init");
                if (init != null && "Assign".equals(init.get("type"))) {
                    String loopVar = (String) init.get("name");
                    if (loopVar != null && !symbols.existsVariable(loopVar)) {
                        symbols.addVariable(loopVar, "entero");
                    }
                }
                analyzeNode(init, symbols, errors);
                Map<String, Object> cond = (Map<String, Object>) node.get("condition");
                String condType = resolveType(cond, symbols, errors);
                if (condType != null && !"entero".equals(condType)) {
                    int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;
                    errors.add(new CompilerError("semantic", line,
                        "La condición del 'para' debe ser 'entero'"));
                }
                analyzeNode((Map<String, Object>) node.get("update"), symbols, errors);
                analyzeNode((Map<String, Object>) node.get("body"), symbols, errors);
            }
            case "PrintStmt" -> resolveType((Map<String, Object>) node.get("expression"), symbols, errors);
            case "Block" -> {
                List<Map<String, Object>> stmts = (List<Map<String, Object>>) node.get("statements");
                if (stmts != null) stmts.forEach(s -> analyzeNode(s, symbols, errors));
            }
            case "EnetroDef" -> {
                String name = (String) node.get("name");
                int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

                if (symbols.existsEnetro(name)) {
                    errors.add(new CompilerError("semantic", line,
                        "ENETRO '" + name + "' ya declarado"));
                    return;
                }

                Map<String, String> columns = new HashMap<>();
                List<Map<String, Object>> fields = (List<Map<String, Object>>) node.get("fields");
                if (fields != null) {
                    for (Map<String, Object> field : fields) {
                        String fName = (String) field.get("name");
                        String fType = (String) field.get("varType");
                        Map<String, Object> fVal = (Map<String, Object>) field.get("value");
                        if (fVal != null) {
                            String valType = resolveType(fVal, symbols, errors);
                            if (valType != null && !valType.equals(fType)) {
                                errors.add(new CompilerError("semantic",
                                    field.get("line") instanceof Number ? ((Number) field.get("line")).intValue() : 0,
                                    "Tipo incompatible en columna '" + fName + "' de ENETRO '" + name + "'"));
                                continue;
                            }
                        }
                        columns.put(fName, fType);
                    }
                }
                symbols.addEnetro(name, columns);
            }
        }
    }

    @SuppressWarnings("unchecked")
    private String resolveType(Map<String, Object> node, SymbolTable symbols, List<CompilerError> errors) {
        if (node == null) return null;
        String type = (String) node.get("type");

        if ("Literal".equals(type)) {
            return (String) node.get("literalType");
        }

        if ("VarRef".equals(type)) {
            String name = (String) node.get("name");
            int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

            if (symbols.existsVariable(name)) {
                return symbols.getVariableType(name);
            }

            String colType = findEnetroColumn(name, symbols);
            if (colType != null) return colType;

            List<String> enetroNames = symbols.getEnetroNames();
            String msg = "Variable '" + name + "' no declarada";
            if (!enetroNames.isEmpty()) {
                msg += ". Tablas ENETRO disponibles: " + String.join(", ", enetroNames);
            }
            errors.add(new CompilerError("semantic", line, msg));
            return null;
        }

        if ("EnetroAccess".equals(type)) {
            String enetroName = (String) node.get("enetroName");
            String fieldName = (String) node.get("fieldName");
            int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

            if (!symbols.existsEnetro(enetroName)) {
                errors.add(new CompilerError("semantic", line,
                    "ENETRO '" + enetroName + "' no declarado"));
                return null;
            }
            if (!symbols.columnExists(enetroName, fieldName)) {
                errors.add(new CompilerError("semantic", line,
                    "Columna '" + fieldName + "' no existe en ENETRO '" + enetroName + "'"));
                return null;
            }
            return symbols.getColumnType(enetroName, fieldName);
        }

        if ("BinOp".equals(type)) {
            return resolveBinOp(node, symbols, errors);
        }

        if ("UnaryOp".equals(type)) {
            String op = (String) node.get("op");
            int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;
            String operandType = resolveType((Map<String, Object>) node.get("operand"), symbols, errors);
            if (operandType == null) return null;
            if (!NUMERIC_TYPES.contains(operandType)) {
                errors.add(new CompilerError("semantic", line,
                    "Operador unario '" + op + "' no válido para tipo '" + operandType + "'"));
                return null;
            }
            return operandType;
        }

        return null;
    }

    @SuppressWarnings("unchecked")
    private String resolveBinOp(Map<String, Object> node, SymbolTable symbols, List<CompilerError> errors) {
        String op = (String) node.get("op");
        int line = node.get("line") instanceof Number ? ((Number) node.get("line")).intValue() : 0;

        String leftType = resolveType((Map<String, Object>) node.get("left"), symbols, errors);
        String rightType = resolveType((Map<String, Object>) node.get("right"), symbols, errors);

        if (leftType == null || rightType == null) return null;

        if ("+".equals(op)) {
            if ("cadena".equals(leftType) && "cadena".equals(rightType)) return "cadena";
            if (leftType.equals(rightType) && NUMERIC_TYPES.contains(leftType)) return leftType;
            errors.add(new CompilerError("semantic", line,
                "'+' no aplicable entre '" + leftType + "' y '" + rightType + "'"));
            return null;
        }

        if ("%".equals(op)) {
            if (!"entero".equals(leftType) || !"entero".equals(rightType)) {
                errors.add(new CompilerError("semantic", line,
                    "'%' solo funciona con 'entero'"));
                return null;
            }
            return "entero";
        }

        if (COMPARISON_OPS.contains(op)) {
            if (!leftType.equals(rightType)) {
                errors.add(new CompilerError("semantic", line,
                    "No se puede comparar '" + leftType + "' con '" + rightType + "'"));
                return null;
            }
            return "entero";
        }

        if (ARITHMETIC_OPS.contains(op)) {
            if (leftType.equals(rightType) && NUMERIC_TYPES.contains(leftType)) return leftType;
            errors.add(new CompilerError("semantic", line,
                "'" + op + "' no válido entre '" + leftType + "' y '" + rightType + "'"));
            return null;
        }

        return null;
    }

    private String findEnetroColumn(String colName, SymbolTable symbols) {
        for (String tableName : symbols.show().keySet()) {
            if (tableName.endsWith(":" + colName)) return symbols.show().get(tableName);
        }
        return null;
    }

    public static class AnalysisResult {
        public final SymbolTable symbolTable;
        public final List<CompilerError> errors;

        public AnalysisResult(SymbolTable symbolTable, List<CompilerError> errors) {
            this.symbolTable = symbolTable;
            this.errors = errors;
        }
    }
}
