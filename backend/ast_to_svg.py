"""
Renderiza el AST como SVG directamente desde Python.
Sin dependencia de Graphviz ni CDN.
Usa layout compacto con Graphviz DOT integrado.
"""



# ── Paleta profesional ─────────────────────────────────────────
NODE_STYLES = {
    'Program':     {'fill': '#2C3E50', 'text': '#FFFFFF'},
    'Block':       {'fill': '#34495E', 'text': '#FFFFFF'},
    'VarDecl':     {'fill': '#27AE60', 'text': '#FFFFFF'},
    'Assign':      {'fill': '#2ECC71', 'text': '#FFFFFF'},
    'BinOp':       {'fill': '#E74C3C', 'text': '#FFFFFF'},
    'UnaryOp':     {'fill': '#C0392B', 'text': '#FFFFFF'},
    'Literal':     {'fill': '#7F8C8D', 'text': '#FFFFFF'},
    'VarRef':      {'fill': '#95A5A6', 'text': '#FFFFFF'},
    'IfStmt':      {'fill': '#E67E22', 'text': '#FFFFFF'},
    'WhileStmt':   {'fill': '#D35400', 'text': '#FFFFFF'},
    'ForStmt':     {'fill': '#F39C12', 'text': '#FFFFFF'},
    'PrintStmt':   {'fill': '#8E44AD', 'text': '#FFFFFF'},
    'EnetroDef':   {'fill': '#2980B9', 'text': '#FFFFFF'},
    'EnetroField': {'fill': '#3498DB', 'text': '#FFFFFF'},
    'EnetroAccess':{'fill': '#1ABC9C', 'text': '#FFFFFF'},
}

DEFAULT_STYLE = {'fill': '#95A5A6', 'text': '#FFFFFF'}

NODE_W = 130
NODE_H = 40
H_SPACING = 12
V_SPACING = 50
PADDING = 30
FONT = 'Segoe UI, system-ui, sans-serif'


def _collect_children(node):
    """Devuelve lista de hijos del nodo."""
    children = []
    for attr in ('statements', 'fields'):
        lst = node.get(attr, [])
        if isinstance(lst, list):
            children.extend(lst)
    for attr in ('condition', 'then_block', 'else_block', 'body',
                 'left', 'right', 'operand', 'expression', 'value',
                 'init', 'update'):
        c = node.get(attr)
        if isinstance(c, dict) and c.get('type'):
            children.append(c)
    return children


def _calc_width(node):
    """Calcula el ancho necesario en unidades de hoja."""
    children = _collect_children(node)
    if not children:
        return 1
    return sum(_calc_width(c) for c in children)


def _layout(node, x_offset, depth, positions, widths):
    """Asigna (x,y) centrado a cada nodo. x_offset en px."""
    w_units = _calc_width(node)
    w_px = w_units * (NODE_W + H_SPACING) - H_SPACING
    x_center = x_offset + w_px / 2
    y = PADDING + depth * (NODE_H + V_SPACING)

    positions.append({
        'node': node,
        'x': x_center,
        'y': y,
        'w': NODE_W,
        'h': NODE_H,
    })

    children = _collect_children(node)
    cx = x_offset
    for child in children:
        cw_units = _calc_width(child)
        cw_px = cw_units * (NODE_W + H_SPACING) - H_SPACING
        _layout(child, cx, depth + 1, positions, widths)
        cx += cw_px + H_SPACING

    return positions


def _node_label(node):
    """Construye etiqueta corta del nodo."""
    ntype = node.get('type', '?')
    parts = []
    name = node.get('name')
    if name:
        parts.append(name)
    var_type = node.get('var_type')
    if var_type:
        parts.append(f'({var_type})')
    op = node.get('op')
    if op:
        parts.append(op)
    val = node.get('value')
    if val is not None and not isinstance(val, (dict, list)):
        s = str(val)
        if len(s) > 16:
            s = s[:13] + '...'
        if node.get('literal_type') == 'cadena':
            s = f'"{s}"'
        parts.append(s)
    label = ' | '.join(parts) if parts else ''
    return ntype, label


def _esc(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


def ast_to_svg(ast_dict):
    """Genera SVG del arbol AST."""
    if not ast_dict:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">'
                '<text x="10" y="30" font-family="sans-serif" font-size="14" fill="#999">'
                '(AST vacio)</text></svg>')

    positions = []
    _layout(ast_dict, PADDING, 0, positions, {})

    if not positions:
        return '<svg/>'

    max_x = max(p['x'] + p['w'] / 2 for p in positions) + PADDING
    max_y = max(p['y'] + p['h'] for p in positions) + PADDING
    svg_w = max(int(max_x), 400)
    svg_h = max(int(max_y), 200)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" '
        f'style="background:#FAFBFC;font-family:{FONT},sans-serif;">',
        '<defs>',
        '  <filter id="s" x="-10%" y="-10%" width="130%" height="130%">'
        '    <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.12"/>'
        '  </filter>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        '    markerWidth="5" markerHeight="5" orient="auto">'
        '    <path d="M0,0 L10,5 L0,10 Z" fill="#BDC3C7"/>'
        '  </marker>',
        '</defs>',
    ]

    # Index para lookup rapido
    pos_map = {id(p['node']): p for p in positions}

    # Aristas
    for p in positions:
        node = p['node']
        nx, ny = p['x'], p['y'] + p['h']
        children = _collect_children(node)
        for child in children:
            cp = pos_map.get(id(child))
            if cp:
                cx, cy = cp['x'], cp['y']
                mid_y = ny + (cy - ny) / 2
                lines.append(
                    f'<path d="M{nx:.0f},{ny:.0f} C{nx:.0f},{mid_y:.0f} '
                    f'{cx:.0f},{mid_y:.0f} {cx:.0f},{cy:.0f}" '
                    f'fill="none" stroke="#BDC3C7" stroke-width="1.5" '
                    f'marker-end="url(#arrow)"/>'
                )

    # Nodos
    for p in positions:
        node = p['node']
        nx, ny = p['x'], p['y']
        ntype, label = _node_label(node)
        style = NODE_STYLES.get(ntype, DEFAULT_STYLE)
        fill = style['fill']
        text_color = style['text']
        x0 = nx - NODE_W / 2

        # Sombra
        lines.append(
            f'<rect x="{x0 + 2:.0f}" y="{ny + 2:.0f}" '
            f'width="{NODE_W}" height="{NODE_H}" rx="6" fill="rgba(0,0,0,0.08)"/>'
        )
        # Cuerpo
        lines.append(
            f'<rect x="{x0:.0f}" y="{ny:.0f}" '
            f'width="{NODE_W}" height="{NODE_H}" rx="6" '
            f'fill="{fill}" stroke="#D5D8DC" stroke-width="1" filter="url(#s)"/>'
        )
        # Tipo
        lines.append(
            f'<text x="{nx:.0f}" y="{ny + 16:.0f}" text-anchor="middle" '
            f'fill="{text_color}" font-size="11" font-weight="700">'
            f'{_esc(ntype)}</text>'
        )
        # Label si es distinto del tipo
        if label and label != ntype:
            lines.append(
                f'<text x="{nx:.0f}" y="{ny + 32:.0f}" text-anchor="middle" '
                f'fill="{text_color}" font-size="9" font-weight="400" '
                f'font-family="Consolas, monospace" opacity="0.85">'
                f'{_esc(label)}</text>'
            )

    lines.append('</svg>')
    return '\n'.join(lines)
