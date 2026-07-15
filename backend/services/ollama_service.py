import requests


def explain_with_llm(code, errors, symbol_table=None):
    try:
        sym_text = ""
        if symbol_table:
            sym_text = "\n".join(
                f"- {name}: {info if isinstance(info, str) else info.get('type', info)}"
                for name, info in symbol_table.items()
            )

        if errors:
            error_list = "\n".join(
                f"- [{e.error_type}] Linea {e.line}: "
                f"{e.message.split('Sugerencia:')[0].strip()}"
                for e in errors
            )

            num_err = len(errors)
            prompt = (
                f"Eres un ingeniero de compiladores senior realizando una "
                f"auditoria tecnica. Responde SIEMPRE en ESPANOL, en texto plano, "
                f"sin markdown ni asteriscos. Usa guiones (-) para listas.\n\n"
                f"CONTEXTO DEL LENGUAJE:\n"
                f"- Tipos estaticos: entero (int), flotante (float), cadena (string).\n"
                f"- Estructuras: si/sino (if/else), mientras (while), para (for), "
                f"imprimir (print), ENETRO (registro/tabla de campos tipados).\n"
                f"- Tipado estatico estricto: sin coercion implicita entre tipos.\n\n"
                f"REGLAS ESTRICTAS:\n"
                f"1. Hay EXACTAMENTE {num_err} error(es) listados en ERRORES. "
                f"Genera EXACTAMENTE {num_err} bloque(s) '--- Error k ---', "
                f"uno por cada error. NO inventes errores adicionales ni repitas "
                f"bloques.\n"
                f"2. Usa SIEMPRE el numero de linea literal que aparece en "
                f"'Linea N:' del compilador. Queda PROHIBIDO usar 0 o lineas "
                f"inventadas; N es el valor real proporcionado.\n"
                f"3. Terminologia tecnica precisa (en espanol o ingles): "
                f"type mismatch (incompatibilidad de tipos), undeclared identifier "
                f"(identificador no declarado), redeclaration (redeclaracion), "
                f"static type checking (verificacion de tipos estatica), symbol "
                f"table (tabla de simbolos), syntax error (error sintactico), "
                f"parse error, unexpected token (token inesperado), scope (ambito).\n"
                f"4. Por cada error, este FORMATO EXACTO:\n\n"
                f"--- Error 1 ---\n"
                f"Tipo: <SemanticError | SyntaxError>\n"
                f"Linea: <N del compilador, verbatim>\n"
                f"Causa: <explicacion tecnica concisa en espanol: que construccion "
                f"viola que regla y por que>\n"
                f"Regla violada: <nombre de la regla semantica/sintactica>\n"
                f"Correccion: <linea(s) corregida(s) con justificacion tecnica>\n\n"
                f"5. No omitas ningun error de la lista. No uses relleno "
                f"('El compilador detecta...'). Ve directo a la causa tecnica.\n"
                f"6. Al terminar el ultimo error, DETENTE. No agregues mas texto.\n\n"
                f"CODIGO:\n{code}\n\n"
                f"ERRORES:\n{error_list}\n\n"
                f"ANALISIS TECNICO (en espanol, exactamente {num_err} error(es), con sus lineas reales):"
            )
        else:
            prompt = (
                "Eres un ingeniero de compiladores senior. Emita un INFORME "
                "TECNICO de compilacion exitosa. Responde SIEMPRE en ESPANOL, "
                "en texto plano, sin markdown ni asteriscos.\n\n"
                "CONTEXTO DEL LENGUAJE:\n"
                "- Tipos estaticos: entero (int), flotante (float), cadena (string).\n"
                "- Estructuras: si/sino, mientras, para, imprimir, ENETRO "
                "(registro de campos tipados).\n\n"
                "REGLAS ESTRICTAS:\n"
                "1. No inventes errores; la compilacion paso todas las fases.\n"
                "2. Terminologia tecnica: static type checking (APROBADA), "
                "symbol table (tabla de simbolos), scope (ambito), AST, "
                "construcciones (if/else, while, for, print, ENETRO).\n"
                "3. Usa EXCLUSIVAMENTE la symbol table del compilador que se "
                "muestra abajo. NO inventes variables ni tipos.\n"
                "4. Formato exacto:\n\n"
                "- Estado: Compilacion exitosa (0 errores)\n"
                "- Verificacion de tipos estatica: APROBADA\n"
                "- Symbol table: <variable>: <tipo> (usar la del compilador)\n"
                "- Construcciones: <ENETRO, if/else, while, for, print usados>\n"
                "- Resumen: <proposito del programa y flujo, conciso y tecnico>\n\n"
                f"CODIGO:\n{code}\n\n"
                f"SYMBOL TABLE (del compilador, fuente de verdad):\n{sym_text}\n\n"
                "INFORME TECNICO:"
            )

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False,
                "keep_alive": 300,
                "options": {
                    "num_predict": 512,
                    "temperature": 0.0
                }
            },
            timeout=(5, 120)
        )

        if response.status_code == 200:
            resp = response.json()["response"]
            return resp.replace("*", "")
        return (
            "El compilador funcionó correctamente, "
            "pero no se pudo obtener la explicación de la IA "
            f"(Error {response.status_code})."
        )

    except requests.exceptions.ConnectionError:
        return (
            "La IA (Ollama) no está disponible en este equipo.\n"
            "El compilador sigue funcionando sin problemas.\n\n"
            "Para activar las explicaciones con IA:\n"
            "  1. Instala Ollama: https://ollama.com\n"
            "  2. Ejecuta: ollama pull gemma3:1b\n"
            "  3. Reinicia el servidor"
        )
    except requests.exceptions.Timeout:
        return ""
    except Exception as e:
        return f"Error al contactar la IA: {str(e)}"
