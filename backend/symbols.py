class SymbolTable:
    def __init__(self):
        self.variables = {}
        self.enetro_tables = {}

    def add_variable(self, name, var_type):
        self.variables[name] = var_type

    def exists_variable(self, name):
        return name in self.variables

    def get_variable_type(self, name):
        return self.variables.get(name)

    def add_enetro(self, name, columns):
        self.enetro_tables[name] = columns

    def exists_enetro(self, name):
        return name in self.enetro_tables

    def column_exists(self, enetro_name, col_name):
        table = self.enetro_tables.get(enetro_name)
        if table is None:
            return False
        return col_name in table

    def get_column_type(self, enetro_name, col_name):
        table = self.enetro_tables.get(enetro_name)
        if table is None:
            return None
        return table.get(col_name)

    def show(self):
        result = {}
        for name, var_type in self.variables.items():
            result[name] = var_type
        for table_name, columns in self.enetro_tables.items():
            for col_name, col_type in columns.items():
                result[f"{table_name}:{col_name}"] = col_type
        return result
