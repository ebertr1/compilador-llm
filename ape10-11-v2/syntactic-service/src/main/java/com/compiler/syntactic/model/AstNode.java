package com.compiler.syntactic.model;

import java.util.*;

public class AstNode extends HashMap<String, Object> {
    public AstNode() {}

    public AstNode(String type) {
        put("type", type);
    }

    @SuppressWarnings("unchecked")
    public List<AstNode> getChildren(String key) {
        Object val = get(key);
        if (val instanceof List) return (List<AstNode>) val;
        List<AstNode> list = new ArrayList<>();
        if (val instanceof AstNode n) list.add(n);
        return list;
    }
}
