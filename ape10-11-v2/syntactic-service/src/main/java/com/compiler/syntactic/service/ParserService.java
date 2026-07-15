package com.compiler.syntactic.service;

import com.compiler.syntactic.grammar.RecursiveDescentParser;
import com.compiler.syntactic.model.*;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class ParserService {

    private final RecursiveDescentParser parser = new RecursiveDescentParser();

    public ParseResponse parse(List<Token> tokens) {
        return parser.parse(tokens);
    }
}
