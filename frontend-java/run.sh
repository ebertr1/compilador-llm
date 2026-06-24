#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Compilador - Frontend JavaFX ==="
echo ""

if [ ! -f "pom.xml" ]; then
    echo "Error: pom.xml no encontrado"
    exit 1
fi

if ! command -v mvn &>/dev/null; then
    echo "Error: Maven no está instalado. Instálalo con:"
    echo "  sudo apt install maven"
    exit 1
fi

echo "Compilando proyecto..."
mvn clean compile -q

echo "Ejecutando interfaz..."
mvn javafx:run -q
