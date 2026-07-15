class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, var_type, name, value, line):
        self.var_type = var_type
        self.name = name
        self.value = value
        self.line = line

class Assign(ASTNode):
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line

class BinOp(ASTNode):
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class UnaryOp(ASTNode):
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line

class Literal(ASTNode):
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type

class VarRef(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class IfStmt(ASTNode):
    def __init__(self, condition, then_block, else_block, line):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.line = line

class WhileStmt(ASTNode):
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body = body
        self.line = line

class ForStmt(ASTNode):
    def __init__(self, init, condition, update, body, line):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
        self.line = line

class PrintStmt(ASTNode):
    def __init__(self, expression, line):
        self.expression = expression
        self.line = line

class EnetroField(ASTNode):
    def __init__(self, var_type, name, value, line):
        self.var_type = var_type
        self.name = name
        self.value = value
        self.line = line

class EnetroDef(ASTNode):
    def __init__(self, name, fields, line):
        self.name = name
        self.fields = fields
        self.line = line

class EnetroAccess(ASTNode):
    def __init__(self, enetro_name, field_name, line):
        self.enetro_name = enetro_name
        self.field_name = field_name
        self.line = line
