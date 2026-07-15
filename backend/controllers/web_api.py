from flask import Flask, request, jsonify, render_template
from controllers.main import get_result
import requests
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/compile', methods=['POST'])
def compile_endpoint():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({
            "success": False,
            "errors": [{"type": "request", "line": 0, "message": "No se envió código"}],
            "symbol_table": {},
            "tokens": [],
            "ast": None,
            "llm_explanation": "Envía el campo 'code' en el JSON."
        }), 400

    code = data['code']
    result = get_result(code)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    ollama_available = False
    models = []
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_available = True
            models = [m['name'] for m in r.json().get('models', [])]
    except Exception:
        pass

    return jsonify({
        "status": "ok",
        "ollama_available": ollama_available,
        "ollama_models": models
    })


@app.route('/examples/<name>', methods=['GET'])
def get_example(name):
    examples_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'examples')
    filepath = os.path.join(examples_dir, name)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify({"code": f.read()})
    return jsonify({"code": ""}), 404


if __name__ == '__main__':
    print("=" * 60)
    print("  Compilador Web - Lenguaje Tipado Estático (ES)")
    print("=" * 60)
    print("  Servidor: http://0.0.0.0:8080")
    print("  Para acceder desde otra máquina:")
    print("  http://<TU_IP>:8080")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=False)
