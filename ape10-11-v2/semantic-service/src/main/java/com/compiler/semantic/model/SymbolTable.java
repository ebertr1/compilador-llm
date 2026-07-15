package com.compiler.semantic.model;

import java.util.*;

public class SymbolTable {
    private final Map<String, String> variables = new HashMap<>();
    private final Map<String, Map<String, String>> enetroTables = new HashMap<>();

    public void addVariable(String name, String type) {
        variables.put(name, type);
    }

    public boolean existsVariable(String name) {
        return variables.containsKey(name);
    }

    public String getVariableType(String name) {
        return variables.get(name);
    }

    public void addEnetro(String name, Map<String, String> columns) {
        enetroTables.put(name, columns);
    }

    public boolean existsEnetro(String name) {
        return enetroTables.containsKey(name);
    }

    public boolean columnExists(String enetroName, String colName) {
        Map<String, String> table = enetroTables.get(enetroName);
        return table != null && table.containsKey(colName);
    }

    public String getColumnType(String enetroName, String colName) {
        Map<String, String> table = enetroTables.get(enetroName);
        return table != null ? table.get(colName) : null;
    }

    public Map<String, String> show() {
        Map<String, String> result = new HashMap<>(variables);
        for (var entry : enetroTables.entrySet()) {
            for (var col : entry.getValue().entrySet()) {
                result.put(entry.getKey() + ":" + col.getKey(), col.getValue());
            }
        }
        return result;
    }

    public boolean hasEnetro(String name) {
        return enetroTables.containsKey(name);
    }

    public List<String> getEnetroNames() {
        return new ArrayList<>(enetroTables.keySet());
    }
}
