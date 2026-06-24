import requests


def explain_with_llm(code, errors):
    try:
        if errors:
            error_list = "\n".join(
                f"- Error en línea {e.line}: {e.message}" for e in errors
            )

            prompt = (
                "Eres un ingeniero senior en compiladores.\n"
                "Responde en español, sin asteriscos, sin caracteres de markdown.\n\n"
                "Recibes una lista de errores reales detectados por el compilador.\n"
                "Analiza UNICAMENTE los errores listados, sin inventar otros.\n"
                "Usa terminología técnica: type mismatch, identificador no declarado,\n"
                "redeclaración, tabla de símbolos, verificación de tipos estática.\n\n"
                "El lenguaje usa tipos en español: entero, flotante, cadena.\n"
                "Las estructuras: si/sino, mientras, para, imprimir, ENETRO.\n\n"
                "Por cada error de la lista, responde con:\n"
                "  Tipo: SemanticError o SyntaxError\n"
                "  Linea: X\n"
                "  Causa: explicación técnica concisa\n"
                "  Regla violada: nombre de la regla semántica violada\n\n"
                "NO analices nada que no esté en la lista.\n"
                "NO uses asteriscos ni markdown. Sangría de 2 espacios.\n"
                "Respuesta clara y técnica en español.\n\n"
                f"CODIGO:\n{code}\n\n"
                f"ERRORES:\n{error_list}\n\n"
                "ANALISIS (solo errores listados):"
            )
        else:
            prompt = (
                "Eres un ingeniero senior en compiladores.\n"
                "Responde en español, sin asteriscos, sin caracteres de markdown.\n\n"
                "El código ha pasado compilación exitosamente.\n"
                "El lenguaje usa tipos en español: entero, flotante, cadena.\n"
                "Las estructuras: si/sino, mientras, para, imprimir, ENETRO.\n\n"
                "Responde con:\n"
                "  Estado: Compilacion exitosa\n"
                "  Tabla de simbolos: variable: tipo, variable: tipo (solo del código)\n"
                "  Verificacion de tipos: APROBADA\n"
                "  Estructuras: descripción breve de ENETRO, condicionales, bucles usados\n\n"
                f"CODIGO:\n{code}\n\n"
                "ANALISIS:"
            )

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 500,
                    "temperature": 0.1
                }
            },
            timeout=(3, 60)
        )

        if response.status_code == 200:
            return response.json()["response"]
        return (
            "El compilador funcionó correctamente, "
            "pero no se pudo obtener la explicación de la IA "
            f"(Error {response.status_code})."
        )

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ La IA (Ollama) no está disponible en este equipo.\n"
            "El compilador sigue funcionando sin problemas.\n\n"
            "Para activar las explicaciones con IA:\n"
            "  1. Instala Ollama: https://ollama.com\n"
            "  2. Ejecuta: ollama pull gemma3:1b\n"
            "  3. Reinicia el servidor"
        )
    except requests.exceptions.Timeout:
        return (
            "⚠️ La IA tardó demasiado en responder.\n"
            "Esto puede ocurrir si el modelo se está cargando.\n"
            "Intenta compilar de nuevo en unos segundos."
        )
    except Exception as e:
        return f"⚠️ Error al contactar la IA: {str(e)}"
