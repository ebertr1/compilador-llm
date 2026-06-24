# Compilador de Lenguaje Tipado Estático

**Escenario 2** — Proyecto universitario APE10-11

---

## Arquitectura del compilador

```
  Código fuente
       │
       ▼
  ┌─────────────┐
  │  LEXER      │  Fase 1: Léxico (PLY lex)
  │  lexer.py   │  Tokeniza: INT, STRING, FLOAT, ID, NUMBER,
  │             │  FLOAT_NUMBER, TEXT, ASSIGN, SEMICOLON,
  │             │  operadores (+, -, *, /, %, relacionales)
  └──────┬──────┘
         │ lista de tokens
         ▼
  ┌─────────────┐
  │  PARSER     │  Fase 2: Sintáctico (PLY yacc)
  │  parser.py  │  Construye AST con gramática libre de
  │             │  contexto y precedencia de operadores
  └──────┬──────┘
         │ AST (Program, VarDecl, Assign, BinOp, ...)
         ▼
  ┌─────────────┐
  │  SEMANTIC   │  Fase 3: Semántico
  │  semantic.py│  - Tabla de símbolos
  │             │  - Verificación de tipos estricta
  │             │  - Variables no declaradas / redeclaradas
  └──────┬──────┘
         │ errores ✓ / tabla de símbolos
         ▼
  ┌─────────────┐
  │  OLLAMA     │  IA Local (Gemma 3 1B)
  │  service.py │  Explica errores y sugiere correcciones
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  WEB API    │  Flask (puerto 8080)
  │  web_api.py │  POST /compile → JSON
  │             │  GET  / → HTML
  └─────────────┘
         │ HTTP (red local)
         ▼
  ┌─────────────────────────────────┐
  │  Navegador web (cualquier PC)   │
  │  http://<IP_SERVIDOR>:8080      │
  └─────────────────────────────────┘
```

---

## Estructura del proyecto

```
APE10-11/
├── backend/
│   ├── ast_nodes.py        # Nodos del AST
│   ├── compiler_error.py   # Dataclass CompilerError
│   ├── lexer.py            # Analizador léxico (PLY)
│   ├── parser.py           # Analizador sintáctico (PLY yacc)
│   ├── semantic.py         # Analizador semántico
│   ├── symbols.py          # Tabla de símbolos
│   ├── ollama_service.py   # Integración con Ollama
│   ├── main.py             # Punto de entrada (CLI + librería)
│   ├── web_api.py          # Servidor web Flask
│   ├── run_server.sh       # Script para iniciar servidor web
│   ├── templates/
│   │   └── index.html      # Interfaz web del compilador
│   └── requirements.txt    # Dependencias Python
├── frontend-java/
│   ├── pom.xml             # Configuración Maven
│   ├── run.sh              # Script de ejecución
│   └── src/main/java/compiler/
│       ├── CompilerGUI.java     # Interfaz JavaFX
│       └── CompilerBackend.java # Puente con Python
├── jflap/
│   ├── AFN.jff             # Autómata Finito No Determinista
│   ├── AFD.jff             # Autómata Finito Determinista
│   └── MIN.jff             # AFD Minimizado
├── examples/
│   ├── correct.txt         # Código válido
│   └── errors.txt          # Código con errores
├── venv/                   # Entorno virtual Python
└── README.md
```

---

## Lenguaje soportado

### Tipos

| Tipo | Declaración | Literales |
|------|-------------|-----------|
| `int` | `int x = 5;` | `5`, `42`, `0` |
| `float` | `float pi = 3.14;` | `3.14`, `0.5` |
| `string` | `string s = "Hola";` | `"texto"` |

### Operadores

| Categoría | Operadores |
|-----------|------------|
| Aritméticos | `+`, `-`, `*`, `/`, `%` |
| Relacionales | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Unario | `-` (negación) |
| Agrupación | `(`, `)` |
| Asignación | `=` |
| String | `+` (concatenación) |

### Reglas de tipos (estrictas)

| Expresión | Tipo | Condición |
|-----------|:----:|-----------|
| `int + int` | `int` | — |
| `int - int` | `int` | — |
| `int * int` | `int` | — |
| `int / int` | `int` | — |
| `int % int` | `int` | — |
| `float + float` | `float` | — |
| `float - float` | `float` | — |
| `float * float` | `float` | — |
| `float / float` | `float` | — |
| `string + string` | `string` | Solo concatenación |
| `int OP float` | **error** | Tipos mixtos no permitidos |
| `string OP int` | **error** | — |
| `x == y`, `x < y`, etc. | `int` | Mismo tipo en ambos lados |
| `-x` (unario) | mismo | Solo `int` o `float` |

### Reglas semánticas

1. **Declaración obligatoria**: toda variable debe declararse con tipo antes de usarse.
2. **Tipado estático estricto**: no hay coerción implícita entre tipos.
   - `int x = 3.14;` → error
   - `float f = 5;` → error
3. **No redeclaración**: una variable no puede declararse dos veces.
4. **Variables no declaradas**: usar una variable no declarada es error.
5. **Operadores**: cada operador verifica tipos específicos.

---

## Fase 1: Léxico (PLY lex)

**Archivo**: `backend/lexer.py`

### Tokens

| Token | Patrón | Ejemplo |
|-------|--------|---------|
| `INT` | `int` | `int` |
| `STRING` | `string` | `string` |
| `FLOAT` | `float` | `float` |
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` | `x`, `nombre` |
| `NUMBER` | `\d+` | `5`, `42` |
| `FLOAT_NUMBER` | `\d+\.\d+` | `3.14`, `0.5` |
| `TEXT` | `"[^"]*"` | `"Hola"` |
| `PLUS` | `\+` | `+` |
| `MINUS` | `-` | `-` |
| `TIMES` | `\*` | `*` |
| `DIVIDE` | `/` | `/` |
| `MOD` | `%` | `%` |
| `EQ` | `==` | `==` |
| `NE` | `!=` | `!=` |
| `LT` | `<` | `<` |
| `GT` | `>` | `>` |
| `LE` | `<=` | `<=` |
| `GE` | `>=` | `>=` |
| `ASSIGN` | `=` | `=` |
| `SEMICOLON` | `;` | `;` |
| `LPAREN` | `(` | `(` |
| `RPAREN` | `)` | `)` |

### Normalización PLN

- Eliminación de espacios y tabs al inicio/fin
- Ignorar comentarios de línea (`#`)
- Ignorar líneas vacías extremas

---

## Fase 2: Sintáctico (PLY yacc)

**Archivo**: `backend/parser.py`

### Gramática (BNF)

```
program     → program statement | statement | ε
statement   → declaration | assignment
declaration → type ID = expression ;
assignment  → ID = expression ;
type        → int | string | float

expression  → comparison
comparison  → comparison EQ additive
            | comparison NE additive
            | comparison LT additive
            | comparison GT additive
            | comparison LE additive
            | comparison GE additive
            | additive
additive    → additive PLUS multiplicative
            | additive MINUS multiplicative
            | multiplicative
multiplicative → multiplicative TIMES unary
               | multiplicative DIVIDE unary
               | multiplicative MOD unary
               | unary
unary       → MINUS unary | primary
primary     → NUMBER | FLOAT_NUMBER | TEXT | ID
            | ( expression )
```

### Precedencia de operadores

```
Mayor:  - (unario)           → derecha
        *, /, %              → izquierda
        +, -                 → izquierda
        <, >, <=, >=         → izquierda
Menor:  ==, !=               → izquierda
```

### AST (Abstract Syntax Tree)

```
ASTNode
├── Program(statements)
├── VarDecl(var_type, name, value, line)
├── Assign(name, value, line)
├── BinOp(left, op, right, line)
├── UnaryOp(op, operand, line)
├── Literal(value, literal_type)
└── VarRef(name, line)
```

---

## Fase 3: Semántico

**Archivo**: `backend/semantic.py`

### Tabla de símbolos (`symbols.py`)

Estructura: `{ nombre_variable: tipo }`

Poblada durante declaraciones, consultada durante asignaciones y expresiones.

### Verificaciones

1. **Redeclaración**: si la variable ya existe en la tabla al declarar → error.
2. **Variable no declarada**: si se usa `VarRef` o `Assign` a variable no registrada → error.
3. **Compatibilidad de tipos**: el tipo de la expresión debe coincidir exactamente con el tipo declarado.
4. **Operadores binarios**: ambos operandos deben ser del mismo tipo y el operador debe ser válido para ese tipo.
5. **Operador unario**: solo aplicable a `int` o `float`.

---

## Integración con IA Local (Ollama + Gemma 3)

**Archivo**: `backend/ollama_service.py`

La IA **no reemplaza** ninguna fase del compilador. Siempre se consulta al finalizar la compilación para:

- ✅ **Si hay errores**: los explica en lenguaje natural y sugiere correcciones.
- ✅ **Si no hay errores**: confirma que el código es correcto.

### Flujo

1. El compilador completa su análisis (léxico → sintáctico → semántico).
2. Siempre se envía el código + resultados a Gemma 3 1B.
3. Gemma devuelve una explicación legible, incluso si no hay errores.

### Instalación de Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:1b
```

> **Nota**: Si Ollama no está disponible, el compilador funciona igual pero sin explicación IA.

---

## Cómo ejecutar

### 🚀 Método principal: Servidor web (para todo el equipo)

En la máquina que tenga Ollama (tu PC), inicia el servidor web. Los demás compañeros acceden desde su navegador.

```bash
# 1. Instalar dependencias (solo una vez)
cd APE10-11/backend
pip install ply requests flask

# 2. (Opcional) Instalar IA — para explicaciones con Gemma 3
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:1b

# 3. Iniciar servidor web
./run_server.sh
```

**Los compañeros acceden en su navegador a:**
```
http://<IP_DEL_SERVIDOR>:8080
```

Para obtener tu IP local: `ip a | grep inet` (busca algo como `192.168.x.x`).

El servidor se ejecuta en `http://0.0.0.0:8080` y es accesible desde toda la red local.

### Alternativa: CLI (sin navegador)

```bash
cd APE10-11/backend

# Modo interactivo
python3 main.py

# Modo JSON
python3 main.py --json < archivo.txt

# Probar con ejemplos
python3 main.py --json < ../examples/correct.txt
python3 main.py --json < ../examples/errors.txt
```

### Alternativa: Frontend JavaFX (offline)

```bash
cd APE10-11/frontend-java
./run.sh
```

---

## Ejemplos de entrada y salida

### Código correcto (`examples/correct.txt`)

**Entrada:**
```
int x = 5;
string nombre = "Juan";
float pi = 3.14;
int resultado = (x + 10) * 2;
float area = pi * 2.0;
string mensaje = nombre + " tiene 20";
int es_mayor = x > 3;
```

**Salida (incluye explicación IA):**
```json
{
  "success": true,
  "errors": [],
  "symbol_table": {
    "x": "int",
    "nombre": "string",
    "pi": "float",
    "resultado": "int",
    "area": "float",
    "mensaje": "string",
    "es_mayor": "int"
  },
  "llm_explanation": "El código es correcto y sin errores."
}
```

### Código con errores (`examples/errors.txt`)

**Entrada:**
```
int y = 10;
y = "texto";
```

**Salida (incluye explicación IA):**
```json
{
  "success": false,
  "errors": [{
    "type": "semantic",
    "line": 2,
    "message": "Error semántico: tipo incompatible. 'y' es 'int' pero la expresión es 'string'"
  }],
  "llm_explanation": "Error semántico en línea 2: intentas asignar un string (\"texto\") a una variable declarada como int. Los tipos son incompatibles. Solución: asigna un número entero: y = 10;"
}
```

### Errores detectados

| Tipo de error | Ejemplo | Mensaje |
|--------------|---------|---------|
| Léxico | `@` | (token ignorado) |
| Sintáctico | `int x = ;` | `Error sintáctico: token inesperado ';'` |
| Sintáctico | `int x = 5` (sin `;`) | `Error sintáctico: token inesperado 'string'` |
| Semántico | `x = "texto"` (x es int) | `Error semántico: tipo incompatible. 'x' es 'int' pero la expresión es 'string'` |
| Semántico | `int z = no_existe` | `Error semántico: variable 'no_existe' no declarada` |
| Semántico | `int x = 5; int x = 10;` | `Error semántico: variable 'x' ya declarada` |
| Semántico | `int a + float b` | `Error semántico: tipos incompatibles 'int' y 'float'` |

---

## Buenas prácticas de estructura de compiladores

1. **Separación de fases**: lexer → parser → semántica. Cada fase es independiente y reemplazable.
2. **AST como intermediario**: el parser produce un AST; la semántica lo recorre. No se mezclan responsabilidades.
3. **Acumulación de errores**: no detenerse en el primer error. Reportar todos los errores posibles.
4. **Tabla de símbolos desacoplada**: estructura separada del análisis semántico.
5. **Precedencia en el parser**: usar la tabla de precedencia de yacc en lugar de modificar la gramática.
6. **IA como herramienta auxiliar**: el LLM solo explica errores, nunca toma decisiones de compilación.
7. **Modo JSON**: permite que cualquier frontend (Java, web, etc.) consuma el compilador.
8. **Manejo de errores robusto**: cada fase captura y reporta errores con línea y mensaje claro.

---

## Autómatas (JFLAP)

Los archivos en `jflap/` representan:

- **AFN.jff**: Autómata Finito No Determinista con transiciones ε que reconoce identificadores, números enteros, flotantes, strings y operadores.
- **AFD.jff**: Autómata Finito Determinista equivalente (sin ε-transiciones).
- **MIN.jff**: AFD minimizado con el menor número de estados posible.

Se pueden abrir con [JFLAP 7.1](http://www.jflap.org/).
