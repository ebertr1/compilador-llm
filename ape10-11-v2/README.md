# APE10-11 v2 — Compilador Microservicios (Java + React)

Reimplementación del compilador de lenguaje tipado estático con español clave como **microservicios Java Spring Boot** con **frontend React**.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (:5173)                  │
│           Monaco Editor + AST Viewer + Tokens           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / WebSocket
                      ▼
┌─────────────────────────────────────────────────────────┐
│              API Gateway Spring Boot (:8080)             │
│              POST /api/compile → Semantic Service        │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Semantic Service (:8083)                    │
│         REST + WebSocket                                 │
│  Orquestador: llama Léxico → Sintáctico → Semántico     │
└────┬──────────────────┬─────────────────────────────────┘
     │ HTTP             │ HTTP
     ▼                  ▼
┌────────────┐   ┌──────────────┐
│  Lexical   │   │  Syntactic   │
│  :8081     │   │  :8082       │
│  DFA       │   │  Recursive   │
│  Tokenizer │   │  Descent     │
└────────────┘   │  Parser      │
                 └──────────────┘
```

## Microservicios

| Servicio | Puerto | Tecnología | Responsabilidad |
|----------|--------|------------|-----------------|
| **Lexical** | 8081 | Spring Boot + DFA Manual | Tokeniza código fuente, retorna tokens + errores |
| **Syntactic** | 8082 | Spring Boot + Recursive Descent | Construye AST desde tokens, retorna árbol + errores |
| **Semantic** | 8083 | Spring Boot + WebSocket | Orquesta pipeline, analiza semántica, retorna resultado completo |
| **API Gateway** | 8080 | Spring Boot | Punto único de entrada, enruta a Semantic Service |
| **Frontend** | 5173 | React + Vite + Monaco | IDE web, visualiza tokens/AST/symbols |

## Flujo de Compilación

```
Código → Léxico → tokens → Sintáctico → AST → Semántico → symbol table → Resultado JSON
         │                   │                    │
         └→ errores          └→ errores           └→ errores
```

1. **Usuario** escribe código en el editor Monaco
2. **Frontend** envía POST `/api/compile` al API Gateway
3. **API Gateway** reenvía al **Semantic Service**
4. **Semantic Service** llama al **Lexical Service** (`POST /lex`) con el código
5. Si hay errores léxicos → retorna inmediatamente
6. Si no, llama al **Syntactic Service** (`POST /parse`) con los tokens
7. Si hay errores sintácticos → retorna inmediatamente
8. Si no, ejecuta el **análisis semántico** localmente (recorre AST)
9. Retorna JSON completo: `{ success, errors[], tokens[], tree{}, symbolTable{}, llmExplanation }`

## Comunicación

| Origen | Destino | Protocolo |
|--------|---------|-----------|
| React | API Gateway | HTTP REST |
| React | Semantic Service | WebSocket (/ws/compile) |
| API Gateway | Semantic Service | HTTP REST |
| Semantic | Lexical | HTTP REST (OkHttp/RestTemplate) |
| Semantic | Syntactic | HTTP REST (OkHttp/RestTemplate) |

## API REST

### POST /api/compile

```json
// Request
{ "code": "entero x = 5;\nimprimir(x);" }

// Response (éxito)
{
  "success": true,
  "errors": [],
  "text": "entero x = 5;\nimprimir(x);",
  "tokens": [
    { "type": "ENTERO", "value": "entero", "line": 1 },
    { "type": "ID", "value": "x", "line": 1 },
    { "type": "ASSIGN", "value": "=", "line": 1 },
    { "type": "NUMBER", "value": "5", "line": 1 },
    { "type": "SEMICOLON", "value": ";", "line": 1 },
    { "type": "IMPRIMIR", "value": "imprimir", "line": 2 },
    { "type": "LPAREN", "value": "(", "line": 2 },
    { "type": "ID", "value": "x", "line": 2 },
    { "type": "RPAREN", "value": ")", "line": 2 },
    { "type": "SEMICOLON", "value": ";", "line": 2 }
  ],
  "tree": {
    "type": "Program",
    "statements": [
      {
        "type": "VarDecl",
        "varType": "entero",
        "name": "x",
        "value": { "type": "Literal", "literalType": "entero", "value": "5" },
        "line": 1
      },
      {
        "type": "PrintStmt",
        "expression": { "type": "VarRef", "name": "x", "line": 2 },
        "line": 2
      }
    ]
  },
  "symbolTable": { "x": "entero" },
  "llmExplanation": "Compilación exitosa. Código correcto."
}
```

## WebSocket

Endpoint: `ws://localhost:8083/ws/compile`

```
→ { "code": "entero x = 5;" }
← { "phase": "lexical", "status": "started" }
← { "phase": "lexical", "status": "done" }
← { "phase": "syntactic", "status": "done" }
← { "phase": "semantic", "status": "done" }
← { "type": "result", "data": { ... resultado completo ... } }
```

## Lenguaje Soportado

### Tipos
- `entero` — Entero de 32 bits
- `flotante` — Punto flotante (64-bit)
- `cadena` — Cadena de texto (inmutable)

### Palabras Reservadas
`entero`, `flotante`, `cadena`, `si`, `sino`, `mientras`, `para`, `imprimir`, `ENETRO`

### Operadores
- Aritméticos: `+`, `-`, `*`, `/`, `%`
- Relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Unario: `-` (negación)
- Asignación: `=`
- Cadena: `+` (concatenación)

### Estructuras
- `si (cond) { ... } sino { ... }`
- `mientras (cond) { ... }`
- `para (init; cond; update) { ... }`
- `imprimir(expr);`
- `ENETRO nombre { tipo campo = valor; ... }`

## Ejecución

### Requisitos
- Java 21+
- Maven 3.9+
- Node.js 18+ (para frontend)

### Iniciar servicios

```bash
# 1. Construir todos los servicios
cd lexical-service && mvn package -DskipTests && cd ..
cd syntactic-service && mvn package -DskipTests && cd ..
cd semantic-service && mvn package -DskipTests && cd ..
cd api-gateway && mvn package -DskipTests && cd ..

# 2. Iniciar servicios (4 terminales)
cd lexical-service && java -jar target/lexical-service-1.0.0.jar
cd syntactic-service && java -jar target/syntactic-service-1.0.0.jar
cd semantic-service && java -jar target/semantic-service-1.0.0.jar
cd api-gateway && java -jar target/api-gateway-1.0.0.jar

# 3. Iniciar frontend
cd frontend && npm install && npm run dev
```

O con Docker:

```bash
docker-compose up --build
```

### Probar con curl

```bash
curl -X POST http://localhost:8080/api/compile \
  -H "Content-Type: application/json" \
  -d '{"code": "entero x = 5;\nimprimir(x);"}'
```

## Decisiones Arquitectónicas

1. **Microservicios Java Spring Boot**: Cada fase del compilador es un servicio independiente y desplegable por separado.
2. **Lexer manual (DFA)**: Sin dependencia de generadores externos (JFlex/ANTLR). Implementación directa para máximo control y mínimo overhead.
3. **Parser Recursivo Descendente**: Sigue exactamente la gramática BNF del proyecto original. Sin generadores, sin tablas LR.
4. **Semántico como Visitor**: Recorre el AST con pattern matching. Desacoplado del parser.
5. **API Gateway**: Punto único de entrada. Aísla al frontend de la topología interna de microservicios.
6. **WebSocket en Semantic**: Permite notificaciones progresivas de fases. No bloquea al cliente.
7. **Cache léxico**: El Semantic cachea resultados del lexical service para código repetido (ConcurrentHashMap).
8. **REST síncrono**: Comunicación directa entre servicios (sin cola de mensajes) para mínima latencia.

## Principios SOLID

- **SRP**: Cada servicio tiene UNA responsabilidad (tokenizar, parsear, analizar, orquestar)
- **OCP**: Nuevas fases (optimización, IR) se agregan sin modificar las existentes
- **LSP**: AstNode es intercambiable por cualquiera de sus tipos
- **ISP**: Cada service expone interfaces mínimas (POST /lex, POST /parse, POST /compile)
- **DIP**: SemanticOrchestrator depende de abstracciones (LexicalServiceClient, SyntacticServiceClient)

## Patrones de Diseño

- **Facade**: `SemanticOrchestrator` simplifica el pipeline completo
- **Strategy**: Las fases del compilador son estrategias intercambiables
- **Visitor**: `SemanticAnalyzer.analyzeNode()` recorre el AST
- **Composite**: El AST es un árbol composite
- **DTO**: `CompileResponse`, `LexResponse`, `ParseResponse`
- **Adapter**: `LexicalServiceClient` y `SyntacticServiceClient` adaptan REST a llamadas locales

## Diagramas UML

Los diagramas se encuentran en `diagrams/` como SVG:

| # | Diagrama | Archivo |
|---|----------|---------|
| 1 | Arquitectura General | `01-architecture-overview.svg` |
| 2 | Componentes | `02-component-diagram.svg` |
| 3 | Despliegue | `03-deployment-diagram.svg` |
| 4 | Paquetes | `04-package-diagram.svg` |
| 5 | Secuencia (Compilación) | `05-sequence-compilation.svg` |
| 6 | Actividades | `06-activity-diagram.svg` |
| 7 | Casos de Uso | `07-usecase-diagram.svg` |
| 8 | Estados | `08-state-diagram.svg` |
| 9 | C4 Contexto | `09-c4-context.svg` |
| 10 | C4 Contenedores | `10-c4-containers.svg` |
| 11 | C4 Componentes | `11-c4-components.svg` |
| 12 | Comunicación MS | `12-communication-diagram.svg` |
| 13 | Flujo de Datos | `13-data-flow.svg` |
| 14 | Clases Léxico | `14-class-lexical.svg` |
| 15 | Clases Sintáctico | `15-class-syntactic.svg` |
| 16 | Clases Semántico | `16-class-semantic.svg` |
| 17 | Clases Modelo AST | `17-class-ast-model.svg` |

Los fuentes PlantUML `.puml` también están disponibles en el mismo directorio.
