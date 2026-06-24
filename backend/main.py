import sys
import json

from lexer import lexer
from parser import parse, syntax_errors
from semantic import SemanticAnalyzer
from ollama_service import explain_with_llm
from compiler_error import CompilerError
from ast_to_dot import ast_to_dot_source
from ast_to_svg import ast_to_svg


def get_tokens(code):
    lexer.lineno = 1
    lexer.input(code)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append({
            "type": tok.type,
            "value": str(tok.value),
            "line": tok.lineno
        })
    return tokens_list


def ast_to_dict(node):
    if node is None:
        return None
    d = {"type": type(node).__name__}
    for attr, value in vars(node).items():
        if attr.startswith('_'):
            continue
        if isinstance(value, list):
            d[attr] = [ast_to_dict(v) for v in value]
        elif hasattr(value, '__dict__'):
            d[attr] = ast_to_dict(value)
        else:
            d[attr] = str(value)
    return d


def compile_code(code):
    code = code.strip()

    lexer.lineno = 1

    tokens_list = get_tokens(code)

    ast = parse(code)

    result = {
        "success": False,
        "errors": [],
        "symbol_table": {},
        "tokens": tokens_list,
        "ast": ast_to_dict(ast),
        "dot": ast_to_dot_source(ast_to_dict(ast)) if ast else "",
        "svg": ast_to_svg(ast_to_dict(ast)) if ast else "",
        "llm_explanation": ""
    }

    if syntax_errors:
        for err in syntax_errors:
            result["errors"].append({
                "type": err.error_type,
                "line": err.line,
                "message": err.message
            })
        result["llm_explanation"] = explain_with_llm(code, syntax_errors)
        return result

    if ast is None:
        result["errors"].append({
            "type": "syntactic",
            "line": 0,
            "message": "No se pudo construir el AST"
        })
        result["llm_explanation"] = explain_with_llm(code, [
            CompilerError("syntactic", 0, 0, "No se pudo construir el AST")
        ])
        return result

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if analyzer.errors:
        for err in analyzer.errors:
            result["errors"].append({
                "type": err.error_type,
                "line": err.line,
                "message": err.message
            })
        result["llm_explanation"] = explain_with_llm(code, analyzer.errors)
        result["symbol_table"] = analyzer.symbols.show()
        return result

    result["success"] = True
    result["symbol_table"] = analyzer.symbols.show()
    result["llm_explanation"] = explain_with_llm(code, [])
    return result


def print_results(result):
    print("=" * 60)
    print("  COMPILADOR - LENGUAJE TIPADO ESTÁTICO (ES)")
    print("=" * 60)

    print("\n--- TOKENS ---")
    for tok in result.get("tokens", []):
        print(f"  {tok['type']:12} '{tok['value']}'  línea {tok['line']}")

    print("\n--- AST ---")
    print(json.dumps(result.get("ast"), indent=2, ensure_ascii=False)[:500])

    if result["success"]:
        print("\n✅ COMPILACIÓN EXITOSA")
        print("\nTabla de símbolos:")
        for name, var_type in result["symbol_table"].items():
            print(f"  {name}: {var_type}")
    else:
        print("\n❌ ERRORES DE COMPILACIÓN")
        for err in result["errors"]:
            print(f"  [{err['type']}] Línea {err['line']}: {err['message']}")

    print("\n--- EXPLICACIÓN LLM ---")
    print(result["llm_explanation"])


def interactive_mode():
    print("Compilador de Lenguaje Tipado Estático (Español)")
    print("Escribe END en una línea sola para finalizar:\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break

    code = "\n".join(lines)
    result = compile_code(code)
    print_results(result)


def json_mode():
    code = sys.stdin.read()
    result = compile_code(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def get_result(code):
    return compile_code(code)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        json_mode()
    else:
        interactive_mode()
