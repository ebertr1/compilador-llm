"""
Genera DOT profesional para el AST del compilador.
Renderizable con @viz-js/viz en el frontend.
Usa etiquetas de texto plano (no HTML) para compatibilidad total.
"""

# ── Paleta profesional ─────────────────────────────────────────
COLORS = {
    'Program':     ('#2C3E50', '#FFFFFF'),
    'Block':       '#34495E',
    'VarDecl':     '#27AE60',
    'Assign':      '#2ECC71',
    'BinOp':       '#E74C3C',
    'UnaryOp':     '#C0392B',
    'Literal':     '#7F8C8D',
    'VarRef':      '#95A5A6',
    'IfStmt':      '#E67E22',
    'WhileStmt':   '#D35400',
    'ForStmt':     '#F39C12',
    'PrintStmt':   '#8E44AD',
    'EnetroDef':   '#2980B9',
    'EnetroField': '#3498DB',
    'EnetroAccess':'#1ABC9C',
}

DEFAULT_COLOR = '#95A5A6'


def _build_label(node):
    """Construye una etiqueta de texto plano para el nodo."""
    node_type = node.get('type', '?')
    parts = [node_type]

    name = node.get('name')
    if name:
        parts.append(name)

    var_type = node.get('var_type')
    if var_type:
        parts.append(f'({var_type})')

    op = node.get('op')
    if op:
        parts.append(op)

    lit_type = node.get('literal_type')
    val = node.get('value')
    if val is not None and not isinstance(val, dict) and not isinstance(val, list):
        sval = str(val)
        if len(sval) > 20:
            sval = sval[:17] + '...'
        if isinstance(val, str) and lit_type == 'cadena':
            sval = f'\\\"{sval}\\\"'
        parts.append(sval)

    label = ' | '.join(parts)
    label = label.replace('"', '\\"')
    return label


def _walk(node, parent_id, graph, counter, depth=0):
    """Recorre el AST recursivamente."""
    if node is None:
        return

    node_id = f"n{counter[0]}"
    counter[0] += 1

    label = _build_label(node)
    node_type = node.get('type', '?')
    bg = COLORS.get(node_type, DEFAULT_COLOR)
    if isinstance(bg, tuple):
        bg, fg = bg
    else:
        fg = '#FFFFFF'

    graph.append(
        f'  {node_id} [label="{label}", fillcolor="{bg}", '
        f'fontcolor="{fg}", style="filled,rounded", shape="box", '
        f'fontname="Segoe UI", fontsize="10", penwidth="1.2", color="#BBBBBB"];'
    )

    if parent_id:
        graph.append(f'  {parent_id} -> {node_id};')

    # Listas de hijos
    for list_attr in ('statements', 'fields'):
        children = node.get(list_attr, [])
        if isinstance(children, list):
            for child in children:
                _walk(child, node_id, graph, counter, depth + 1)

    # Atributos individuales
    for attr in ('condition', 'then_block', 'else_block', 'body',
                 'left', 'right', 'operand', 'expression',
                 'value', 'init', 'update'):
        child = node.get(attr)
        if isinstance(child, dict) and child.get('type'):
            _walk(child, node_id, graph, counter, depth + 1)


def ast_to_dot_source(ast_dict):
    """Genera código DOT profesional."""
    lines = [
        'digraph AST {',
        '  rankdir=TB;',
        '  bgcolor="#FAFBFC";',
        '  node [fontname="Segoe UI", fontsize="10", margin="0.08,0.04"];',
        '  edge [color="#95A5A6", arrowhead="vee", arrowsize="0.6", penwidth="0.8"];',
        '  graph [dpi=150, splines=true, pad="0.5", nodesep="0.3", ranksep="0.4"];',
        '',
    ]
    _walk(ast_dict, None, lines, [0])
    lines.append('}')
    return '\n'.join(lines)
