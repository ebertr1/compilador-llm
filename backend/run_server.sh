#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activar virtualenv si existe
VENV_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/venv"
if [ -f "$VENV_DIR/bin/activate" ]; then
    . "$VENV_DIR/bin/activate"
fi

echo "========================================================"
echo "  Compilador Web - Lenguaje Tipado Estático"
echo "========================================================"
echo ""

# Verificar Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 no está instalado."
    exit 1
fi

# Verificar dependencias
echo "[1/3] Verificando dependencias..."
pip install -q flask ply requests 2>/dev/null || pip3 install -q flask ply requests 2>/dev/null

# Verificar Ollama
echo "[2/3] Verificando Ollama..."
python3 << 'PYEOF' 2>&1 || true
import requests
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=3)
    if r.status_code == 200:
        models = [m['name'] for m in r.json().get('models', [])]
        print(f'    Ollama disponible. Modelos: {models}')
        if 'gemma3:1b' in models:
            print('    \U0001f7e2 Modelo gemma3:1b listo')
        else:
            print('    \u26a0\ufe0f  Ejecuta: ollama pull gemma3:1b')
    else:
        print('    \u26a0\ufe0f  Ollama respondio con codigo ' + str(r.status_code))
except Exception as e:
    print(f'    \u26a0\ufe0f  Ollama no disponible ({e})')
    print('    El compilador funciona sin IA.')
    print('    Para activar IA: ollama pull gemma3:1b')
PYEOF

echo ""
echo "[3/3] Iniciando servidor web..."
echo "========================================================"
echo "  Servidor: http://0.0.0.0:8080"
echo ""
echo "  Para acceder desde otra máquina en la red:"
echo "  1. Obtén tu IP local: ip a | grep inet"
echo "  2. Abre en el navegador: http://<TU_IP>:8080"
echo ""
echo "  Para detener: Ctrl+C"
echo "========================================================"
echo ""

python3 -m controllers.web_api
