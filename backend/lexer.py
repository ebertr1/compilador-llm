import ply.lex as lex

reserved = {
    'entero': 'ENTERO',
    'flotante': 'FLOTANTE',
    'cadena': 'CADENA',
    'si': 'SI',
    'sino': 'SINO',
    'mientras': 'MIENTRAS',
    'para': 'PARA',
    'imprimir': 'IMPRIMIR',
    'ENETRO': 'ENETRO',
}

tokens = [
    'ID', 'NUMBER', 'FLOAT_NUMBER', 'TEXT',
    'ASSIGN', 'SEMICOLON',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'COMMA', 'DOT',
] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_DOT = r'\.'

t_ASSIGN = r'='
t_SEMICOLON = r';'

t_ignore = ' \t'


def t_LE(t):
    r'<='
    return t


def t_GE(t):
    r'>='
    return t


def t_EQ(t):
    r'=='
    return t


def t_NE(t):
    r'!='
    return t


def t_LT(t):
    r'<'
    return t


def t_GT(t):
    r'>'
    return t


def t_FLOAT_NUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_TEXT(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    if t.type == 'ID' and t.value != t.value.lower():
        upper = t.value.upper()
        if upper in reserved:
            t.type = upper
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_comment_hash(t):
    r'\#.*'
    pass


def t_comment_slash(t):
    r'//.*'
    pass


def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex()
