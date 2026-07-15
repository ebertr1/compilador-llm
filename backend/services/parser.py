import ply.yacc as yacc
from services.lexer import tokens
from models.ast_nodes import (
    Program, VarDecl, Assign, BinOp, UnaryOp, Literal, VarRef,
    Block, IfStmt, WhileStmt, ForStmt, PrintStmt,
    EnetroDef, EnetroField, EnetroAccess
)
from models.compiler_error import CompilerError

syntax_errors = []

precedence = (
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),
)


def p_program(p):
    '''
    program : program statement
            | statement
            | empty
    '''
    if len(p) == 3 and isinstance(p[1], Program):
        p[0] = Program(p[1].statements + [p[2]])
    elif len(p) == 3 and p[1] is None:
        p[0] = Program([p[2]])
    elif len(p) == 2 and p[1] is not None:
        p[0] = Program([p[1]])
    else:
        p[0] = Program([])


def p_empty(p):
    'empty :'
    pass


def p_statement_declaration(p):
    '''
    statement : type ID ASSIGN expression SEMICOLON
    '''
    p[0] = VarDecl(p[1], p[2], p[4], p.lineno(2))


def p_statement_plain_declaration(p):
    '''
    statement : type ID SEMICOLON
    '''
    p[0] = VarDecl(p[1], p[2], None, p.lineno(2))


def p_statement_assignment(p):
    '''
    statement : ID ASSIGN expression SEMICOLON
    '''
    p[0] = Assign(p[1], p[3], p.lineno(1))


def p_type_entero(p):
    'type : ENTERO'
    p[0] = 'entero'


def p_type_flotante(p):
    'type : FLOTANTE'
    p[0] = 'flotante'


def p_type_cadena(p):
    'type : CADENA'
    p[0] = 'cadena'


def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MOD expression
               | expression EQ expression
               | expression NE expression
               | expression LT expression
               | expression GT expression
               | expression LE expression
               | expression GE expression
    '''
    p[0] = BinOp(p[1], p[2], p[3], p.lineno(2))


def p_expression_group(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2]


def p_expression_unary(p):
    '''
    expression : MINUS expression %prec UMINUS
    '''
    p[0] = UnaryOp(p[1], p[2], p.lineno(1))


def p_expression_literal_int(p):
    'expression : NUMBER'
    p[0] = Literal(p[1], 'entero')


def p_expression_literal_float(p):
    'expression : FLOAT_NUMBER'
    p[0] = Literal(p[1], 'flotante')


def p_expression_literal_string(p):
    'expression : TEXT'
    p[0] = Literal(p[1], 'cadena')


def p_expression_variable(p):
    'expression : ID'
    p[0] = VarRef(p[1], p.lineno(1))


def p_expression_enetro_access(p):
    '''
    expression : ID DOT ID
    '''
    p[0] = EnetroAccess(p[1], p[3], p.lineno(1))


def p_statement_if(p):
    '''
    statement : SI LPAREN expression RPAREN block
              | SI LPAREN expression RPAREN block SINO block
    '''
    if len(p) == 6:
        p[0] = IfStmt(p[3], p[5], None, p.lineno(1))
    else:
        p[0] = IfStmt(p[3], p[5], p[7], p.lineno(1))


def p_statement_while(p):
    '''
    statement : MIENTRAS LPAREN expression RPAREN block
    '''
    p[0] = WhileStmt(p[3], p[5], p.lineno(1))


def p_statement_for(p):
    '''
    statement : PARA LPAREN for_init SEMICOLON expression SEMICOLON for_update RPAREN block
    '''
    p[0] = ForStmt(p[3], p[5], p[7], p[9], p.lineno(1))


def p_for_init(p):
    '''
    for_init : ID ASSIGN expression
    '''
    p[0] = Assign(p[1], p[3], p.lineno(1))


def p_for_update(p):
    '''
    for_update : ID ASSIGN expression
    '''
    p[0] = Assign(p[1], p[3], p.lineno(1))


def p_statement_print(p):
    '''
    statement : IMPRIMIR LPAREN expression RPAREN SEMICOLON
    '''
    p[0] = PrintStmt(p[3], p.lineno(1))


def p_statement_enetro_def(p):
    '''
    statement : ENETRO ID LBRACE enetro_fields RBRACE
    '''
    p[0] = EnetroDef(p[2], p[4], p.lineno(2))


def p_enetro_fields_single(p):
    '''
    enetro_fields : enetro_field
    '''
    p[0] = [p[1]]


def p_enetro_fields_multi(p):
    '''
    enetro_fields : enetro_fields enetro_field
    '''
    p[0] = p[1] + [p[2]]


def p_enetro_field_valued(p):
    '''
    enetro_field : type ID ASSIGN expression SEMICOLON
    '''
    p[0] = EnetroField(p[1], p[2], p[4], p.lineno(2))


def p_enetro_field_plain(p):
    '''
    enetro_field : type ID SEMICOLON
    '''
    p[0] = EnetroField(p[1], p[2], None, p.lineno(2))


def p_block(p):
    '''
    block : LBRACE program RBRACE
    '''
    p[0] = Block(p[2].statements if p[2] else [])


def p_single_statement_block(p):
    '''
    block : statement
    '''
    if isinstance(p[1], Block):
        p[0] = p[1]
    else:
        p[0] = Block([p[1]])


def p_error(p):
    if p is None:
        syntax_errors.append(CompilerError(
            'syntactic', 0, 0,
            "Error sintáctico: el archivo termina de forma inesperada. "
            "Revisa que todas las declaraciones, expresiones, llaves y "
            "paréntesis estén completos y terminados con punto y coma ';'."
        ))
        return

    if p.type in ('ID', 'ENTERO', 'FLOTANTE', 'CADENA', 'SI', 'SINO',
                  'MIENTRAS', 'PARA', 'IMPRIMIR', 'ENETRO'):
        syntax_errors.append(CompilerError(
            'syntactic', p.lineno, 0,
            f"Error sintáctico: falta punto y coma ';' al final de la "
            f"instrucción anterior. Se encontró '{p.value}' de forma "
            f"inesperada en línea {p.lineno}."
        ))
    elif p.type == 'RBRACE':
        syntax_errors.append(CompilerError(
            'syntactic', p.lineno, 0,
            f"Error sintáctico: llave de cierre '}}' inesperada en línea "
            f"{p.lineno}. Revisa que todas las llaves estén correctamente "
            f"balanceadas y que no falte punto y coma ';' antes de cerrar."
        ))
    elif p.type == 'RPAREN':
        syntax_errors.append(CompilerError(
            'syntactic', p.lineno, 0,
            f"Error sintáctico: paréntesis ')' inesperado en línea "
            f"{p.lineno}. Revisa que los paréntesis estén correctamente "
            f"balanceados."
        ))
    elif p.type == 'SEMICOLON':
        syntax_errors.append(CompilerError(
            'syntactic', p.lineno, 0,
            f"Error sintáctico: punto y coma ';' inesperado en línea "
            f"{p.lineno}. Revisa que no haya un ';' de más."
        ))
    else:
        syntax_errors.append(CompilerError(
            'syntactic', p.lineno, 0,
            f"Error sintáctico: token inesperado '{p.value}' en línea "
            f"{p.lineno}. Revisa la sintaxis de la instrucción."
        ))


parser = yacc.yacc(start='program', write_tables=False, debug=False)


def parse(code):
    global syntax_errors
    syntax_errors.clear()
    result = parser.parse(code)
    return result
