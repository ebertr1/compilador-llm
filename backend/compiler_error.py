from dataclasses import dataclass

@dataclass
class CompilerError:
    error_type: str
    line: int
    column: int
    message: str
