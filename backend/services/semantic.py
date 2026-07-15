from models.symbols import SymbolTable
from models.compiler_error import CompilerError
from models.ast_nodes import (
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
                    f"Error semántico: variable '{node.name}' ya declarada. "
                    f"Sugerencia: usa un nombre diferente o elimina la "
                    f"declaración anterior."
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
                    f"Error semántico: tipo incompatible en declaración de "
                    f"'{node.name}'. La variable es '{node.var_type}' pero "
                    f"se asignó un valor de tipo '{expr_type}'. Sugerencia: "
                    f"cambia el tipo de la variable a '{expr_type}' o "
                    f"asigna un valor de tipo '{node.var_type}'."
                ))
                return

            self.symbols.add_variable(node.name, node.var_type)

        elif isinstance(node, Assign):
            if not self.symbols.exists_variable(node.name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: variable '{node.name}' no declarada. "
                    f"Sugerencia: declara la variable con 'entero', "
                    f"'flotante' o 'cadena' antes de usarla."
                ))
                return

            var_type = self.symbols.get_variable_type(node.name)
            expr_type = self._resolve_type(node.value)

            if expr_type is None:
                return

            if expr_type != var_type:
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: tipo incompatible en asignación a "
                    f"'{node.name}'. La variable es '{var_type}' pero la "
                    f"expresión es '{expr_type}'. Sugerencia: asigna un "
                    f"valor de tipo '{var_type}'."
                ))

        elif isinstance(node, IfStmt):
            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'si' debe ser de tipo "
                    f"'entero', pero se usó '{cond_type}'. Sugerencia: usa "
                    f"una expresión que devuelva 'entero' (por ejemplo: "
                    f"x > 0, x == 1, x)."
                ))
            self.analyze(node.then_block)
            if node.else_block:
                self.analyze(node.else_block)

        elif isinstance(node, WhileStmt):
            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'mientras' debe ser de tipo "
                    f"'entero', pero se usó '{cond_type}'. Sugerencia: usa "
                    f"una expresión que devuelva 'entero' (por ejemplo: "
                    f"x < 5, x != 0, x)."
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
                            f"del 'para'. Se esperaba '{var_type}' pero la "
                            f"expresión es '{init_type}'. Sugerencia: asigna "
                            f"un valor de tipo '{var_type}'."
                        ))

            cond_type = self._resolve_type(node.condition)
            if cond_type is not None and cond_type != 'entero':
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la condición del 'para' debe ser de tipo "
                    f"'entero', pero se usó '{cond_type}'. Sugerencia: usa "
                    f"una expresión que devuelva 'entero' (por ejemplo: "
                    f"i < 10, i != 0)."
                ))

            if isinstance(node.update, Assign):
                if not self.symbols.exists_variable(node.update.name):
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: variable '{node.update.name}' "
                        f"no declarada en la actualización del 'para'. "
                        f"Sugerencia: la variable debe declararse antes "
                        f"de usarla en el bucle 'para'."
                    ))
                else:
                    upd_type = self._resolve_type(node.update.value)
                    var_type = self.symbols.get_variable_type(node.update.name)
                    if upd_type is not None and upd_type != var_type:
                        self.errors.append(CompilerError(
                            'semantic', node.line, 0,
                            f"Error semántico: tipo incompatible en la "
                            f"actualización del 'para'. Se esperaba "
                            f"'{var_type}' pero la expresión es "
                            f"'{upd_type}'. Sugerencia: asigna un valor "
                            f"de tipo '{var_type}'."
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
                    f"Error semántico: ENETRO '{node.name}' ya declarado. "
                    f"Sugerencia: usa un nombre diferente para la tabla."
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
                            f"Se esperaba '{field.var_type}' y se recibió "
                            f"'{val_type}'. Sugerencia: asigna un valor "
                            f"de tipo '{field.var_type}' a la columna."
                        ))
                        continue
                columns[field.name] = field.var_type

            self.symbols.add_enetro(node.name, columns)

        elif isinstance(node, EnetroAccess):
            if not self.symbols.exists_enetro(node.enetro_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: ENETRO '{node.enetro_name}' no declarado. "
                    f"Sugerencia: define la tabla ENETRO antes de usarla."
                ))
                return None

            if not self.symbols.column_exists(node.enetro_name, node.field_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la columna '{node.field_name}' no existe "
                    f"en ENETRO '{node.enetro_name}'. Sugerencia: revisa "
                    f"los nombres de las columnas definidas en el ENETRO."
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
                msg = (
                    f"Error semántico: variable '{node.name}' no declarada. "
                    f"Sugerencia: declara la variable con 'entero', "
                    f"'flotante' o 'cadena' antes de usarla."
                )
                if enetro_names:
                    msg += (
                        f" ¿Olvidaste el prefijo de la tabla ENETRO? "
                        f"Tablas disponibles: {', '.join(enetro_names)}."
                    )
                self.errors.append(CompilerError(
                    'semantic', node.line, 0, msg
                ))
                return None
            return self.symbols.get_variable_type(node.name)

        elif isinstance(node, EnetroAccess):
            if not self.symbols.exists_enetro(node.enetro_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: ENETRO '{node.enetro_name}' no "
                    f"declarado. Sugerencia: define la tabla ENETRO "
                    f"antes de usarla."
                ))
                return None
            if not self.symbols.column_exists(node.enetro_name, node.field_name):
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la columna '{node.field_name}' no "
                    f"existe en ENETRO '{node.enetro_name}'. Sugerencia: "
                    f"revisa los nombres de las columnas definidas en el "
                    f"ENETRO."
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
                    f"Error semántico: la operación '+' no se puede aplicar "
                    f"entre '{left_type}' y '{right_type}'. Sugerencia: "
                    f"ambos operandos deben ser del mismo tipo (numérico "
                    f"para suma, 'cadena' para concatenación)."
                ))
                return None

            if node.op == '%':
                if left_type != 'entero' or right_type != 'entero':
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: el operador '%' (módulo) solo "
                        f"funciona con tipo 'entero', no entre "
                        f"'{left_type}' y '{right_type}'. Sugerencia: "
                        f"asegúrate de que ambos operandos sean 'entero'."
                    ))
                    return None
                return 'entero'

            if node.op in COMPARISON_OPS:
                if left_type != right_type:
                    self.errors.append(CompilerError(
                        'semantic', node.line, 0,
                        f"Error semántico: no se puede comparar "
                        f"'{left_type}' con '{right_type}'. Sugerencia: "
                        f"solo se pueden comparar valores del mismo tipo."
                    ))
                    return None
                return 'entero'

            if node.op in ARITHMETIC_OPS:
                if left_type == right_type and left_type in NUMERIC_TYPES:
                    return left_type
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: la operación '{node.op}' no es válida "
                    f"entre '{left_type}' y '{right_type}'. Sugerencia: "
                    f"ambos operandos deben ser del mismo tipo numérico "
                    f"('entero' o 'flotante')."
                ))
                return None

            self.errors.append(CompilerError(
                'semantic', node.line, 0,
                f"Error semántico: tipos incompatibles "
                f"'{left_type}' y '{right_type}'. Sugerencia: revisa "
                f"que los tipos de ambos operandos coincidan."
            ))
            return None

        elif isinstance(node, UnaryOp):
            operand_type = self._resolve_type(node.operand)
            if operand_type is None:
                return None
            if operand_type not in NUMERIC_TYPES:
                self.errors.append(CompilerError(
                    'semantic', node.line, 0,
                    f"Error semántico: el operador unario '{node.op}' "
                    f"no es válido para tipo '{operand_type}'. Sugerencia: "
                    f"el operador '{node.op}' solo se aplica a valores "
                    f"numéricos ('entero' o 'flotante')."
                ))
                return None
            return operand_type

        return None
