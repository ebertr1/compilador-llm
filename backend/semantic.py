from symbols import SymbolTable
from compiler_error import CompilerError
from ast_nodes import (
    Program, VarDecl, Assign, BinOp, UnaryOp, Literal, VarRef,
    Block, IfStmt, WhileStmt, ForStmt, PrintStmt,
    EnetroDef, EnetroField, EnetroAccess
)


NUMERIC_TYPES = ('entero', 'flotante')
COMPARISON_OPS = ('==', '!=', '<', '>', '<=', '>=')
ARITHMETIC_OPS = ('+', '-', '*', '/')


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()
        self.errors = []

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)

        elif isinstance(node, VarDecl):
            if self.symbols.exists_variable(node.name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: variable '{node.name}' ya declarada"
                ))
                return

            if node.value is None:
                self.symbols.add_variable(node.name, node.var_type)
                return

            expr_type = self._resolve_type(node.value)
            if expr_type is None:
                return

            if expr_type != node.var_type:
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: tipo incompatible. '{node.name}' es "
                    f"'{node.var_type}' pero la expresión es '{expr_type}'"
                ))
                return

            self.symbols.add_variable(node.name, node.var_type)

        elif isinstance(node, Assign):
            if not self.symbols.exists_variable(node.name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: variable '{node.name}' no declarada"
                ))
                return

            var_type = self.symbols.get_variable_type(node.name)
            expr_type = self._resolve_type(node.value)

            if expr_type is None:
                return

            if expr_type != var_type:
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: tipo incompatible. '{node.name}' es "
                    f"'{var_type}' pero la expresión es '{expr_type}'"
                ))

        elif isinstance(node, IfStmt):
            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'si' debe ser entero, "
                    f"no '{cond_type}'"
                ))
            self.analyze(node.then_block)
            if node.else_block:
                self.analyze(node.else_block)

        elif isinstance(node, WhileStmt):
            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'mientras' debe ser entero, "
                    f"no '{cond_type}'"
                ))
            self.analyze(node.body)

        elif isinstance(node, ForStmt):
            if isinstance(node.init, Assign):
                if not self.symbols.exists_variable(node.init.name):
                    init_type = self._resolve_type(node.init.value)
                    if init_type is not None:
                        self.symbols.add_variable(node.init.name, init_type)
                else:
                    init_type = self._resolve_type(node.init.value)
                    var_type = self.symbols.get_variable_type(node.init.name)
                    if init_type is not None and init_type != var_type:
                        self.errors.append(CompilerError(
                            'semantic', node.line, 0,
                            f"Error semántico: tipo incompatible en inicialización "
                            f"del 'para'"
                        ))

            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'para' debe ser entero, "
                    f"no '{cond_type}'"
                ))

            if isinstance(node.update, Assign):
                if not self.symbols.exists_variable(node.update.name):
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: variable '{node.update.name}' "
                        f"no declarada en actualización del 'para'"
                    ))
                else:
                    upd_type = self._resolve_type(node.update.value)
                    var_type = self.symbols.get_variable_type(node.update.name)
                    if upd_type is not None and upd_type != var_type:
                        self.errors.append(CompilerError(
                            'semantic', node.line, 0,
                            f"Error semántico: tipo incompatible en actualización "
                            f"del 'para'"
                        ))

            self.analyze(node.body)

        elif isinstance(node, PrintStmt):
            self._resolve_type(node.expression)

        elif isinstance(node, Block):
            for stmt in node.statements:
                self.analyze(stmt)

        elif isinstance(node, EnetroDef):
            if self.symbols.exists_enetro(node.name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: ENETRO '{node.name}' ya declarado"
                ))
                return

            columns = {}
            for field in node.fields:
                if field.value is not None:
                    val_type = self._resolve_type(field.value)
                    if val_type is not None and val_type != field.var_type:
                        self.errors.append(CompilerError(
                            'semantic', field.line, 0,
                            f"Error semántico: tipo incompatible en columna "
                            f"'{field.name}' de ENETRO '{node.name}'. "
                            f"Se esperaba '{field.var_type}' y se recibió '{val_type}'"
                        ))
                        continue
                columns[field.name] = field.var_type

            self.symbols.add_enetro(node.name, columns)

        elif isinstance(node, EnetroAccess):
            if not self.symbols.exists_enetro(node.enetro_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: ENETRO '{node.enetro_name}' no declarado"
                ))
                return None

            if not self.symbols.column_exists(node.enetro_name, node.field_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la columna '{node.field_name}' no existe "
                    f"en ENETRO '{node.enetro_name}'"
                ))
                return None

    def _find_enetro_column(self, col_name):
        for table_name in self.symbols.enetro_tables:
            if self.symbols.column_exists(table_name, col_name):
                return self.symbols.get_column_type(table_name, col_name)
        return None

    def _resolve_type(self, node):
        if isinstance(node, Literal):
            return node.literal_type

        elif isinstance(node, VarRef):
            if not self.symbols.exists_variable(node.name):
                col_type = self._find_enetro_column(node.name)
                if col_type:
                    return col_type
                enetro_names = list(self.symbols.enetro_tables.keys())
                msg = f"Error semántico: variable '{node.name}' no declarada"
                if enetro_names:
                    msg += f". ¿Olvidaste el prefijo de ENETRO? Tablas: {', '.join(enetro_names)}"
                self.errors.append(CompilerError(
                    'semantic', node.line, 0, msg
                ))
                return None
            return self.symbols.get_variable_type(node.name)

        elif isinstance(node, EnetroAccess):
            if not self.symbols.exists_enetro(node.enetro_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: ENETRO '{node.enetro_name}' no declarado"
                ))
                return None
            if not self.symbols.column_exists(node.enetro_name, node.field_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la columna '{node.field_name}' no existe "
                    f"en ENETRO '{node.enetro_name}'"
                ))
                return None
            return self.symbols.get_column_type(node.enetro_name, node.field_name)

        elif isinstance(node, BinOp):
            left_type = self._resolve_type(node.left)
            right_type = self._resolve_type(node.right)

            if left_type is None or right_type is None:
                return None

            if node.op == '+':
                if left_type == 'cadena' and right_type == 'cadena':
                    return 'cadena'
                if left_type == right_type and left_type in NUMERIC_TYPES:
                    return left_type
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: operación '+' inválida entre "
                    f"'{left_type}' y '{right_type}'"
                ))
                return None

            if node.op == '%':
                if left_type != 'entero' or right_type != 'entero':
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: '%' solo válido para 'entero', "
                        f"no entre '{left_type}' y '{right_type}'"
                    ))
                    return None
                return 'entero'

            if node.op in COMPARISON_OPS:
                if left_type != right_type:
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: no se puede comparar "
                        f"'{left_type}' con '{right_type}'"
                    ))
                    return None
                return 'entero'

            if node.op in ARITHMETIC_OPS:
                if left_type == right_type and left_type in NUMERIC_TYPES:
                    return left_type
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: operación '{node.op}' inválida entre "
                    f"'{left_type}' y '{right_type}'"
                ))
                return None

            self.errors.append(CompilerError(
                'semantic', node.line, 0,
                f"Error semántico: tipos incompatibles '{left_type}' y '{right_type}'"
            ))
            return None

        elif isinstance(node, UnaryOp):
            operand_type = self._resolve_type(node.operand)
            if operand_type is None:
                return None
            if operand_type not in NUMERIC_TYPES:
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: no se puede aplicar '{node.op}' "
                    f"a tipo '{operand_type}'"
                ))
                return None
            return operand_type

        return None
