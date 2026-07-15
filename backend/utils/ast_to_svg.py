"""
Renderiza el AST como SVG profesional directamente desde Python.
Sin dependencia de Graphviz ni CDN.
Layout automático con curvas Bezier, sombras, leyenda de colores.
"""

NODE_STYLES = {
    'Program':     {'fill': '#2C3E50', 'text': '#FFFFFF', 'border': '#1A252F'},
    'Block':       {'fill': '#34495E', 'text': '#FFFFFF', 'border': '#2C3E50'},
    'VarDecl':     {'fill': '#27AE60', 'text': '#FFFFFF', 'border': '#1E8449'},
    'Assign':      {'fill': '#2ECC71', 'text': '#FFFFFF', 'border': '#1DBB64'},
    'BinOp':       {'fill': '#E74C3C', 'text': '#FFFFFF', 'border': '#C0392B'},
    'UnaryOp':     {'fill': '#C0392B', 'text': '#FFFFFF', 'border': '#A93226'},
    'Literal':     {'fill': '#7F8C8D', 'text': '#FFFFFF', 'border': '#6C7A7D'},
    'VarRef':      {'fill': '#95A5A6', 'text': '#FFFFFF', 'border': '#7F8C8D'},
    'IfStmt':      {'fill': '#E67E22', 'text': '#FFFFFF', 'border': '#D35400'},
    'WhileStmt':   {'fill': '#D35400', 'text': '#FFFFFF', 'border': '#BA4A00'},
    'ForStmt':     {'fill': '#F39C12', 'text': '#FFFFFF', 'border': '#D68910'},
    'PrintStmt':   {'fill': '#8E44AD', 'text': '#FFFFFF', 'border': '#6C3483'},
    'EnetroDef':   {'fill': '#2980B9', 'text': '#FFFFFF', 'border': '#1F6DA0'},
    'EnetroField': {'fill': '#3498DB', 'text': '#FFFFFF', 'border': '#2E86C1'},
    'EnetroAccess':{'fill': '#1ABC9C', 'text': '#FFFFFF', 'border': '#17A589'},
}

DEFAULT_STYLE = {'fill': '#95A5A6', 'text': '#FFFFFF', 'border': '#7F8C8D'}

FONT = 'Segoe UI, system-ui, sans-serif'
FONT_MONO = 'Consolas, "JetBrains Mono", monospace'
NODE_MIN_W = 110
NODE_H = 44
H_SPACING = 16
V_SPACING = 56
PADDING = 40
LEGEND_W = 200


def _collect_children(node):
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


def _node_label(node):
    ntype = node.get('type', '?')
    parts = []
    name = node.get('name')
    if name:
        parts.append(str(name))
    var_type = node.get('var_type')
    if var_type:
        parts.append(f'({var_type})')
    op = node.get('op')
    if op:
        parts.append(str(op))
    val = node.get('value')
    if val is not None and not isinstance(val, (dict, list)):
        s = str(val)
        if len(s) > 22:
            s = s[:19] + '...'
        if node.get('literal_type') == 'cadena':
            s = f'"{s}"'
        parts.append(s)
    return ntype, ' | '.join(parts) if parts else ''


def _measure_label(ntype, label):
    max_chars = max(len(ntype), len(label)) if label else len(ntype)
    return max(NODE_MIN_W, max_chars * 7 + 24)


def _calc_width(node, cache):
    key = id(node)
    if key in cache:
        return cache[key]
    children = _collect_children(node)
    if not children:
        ntype, label = _node_label(node)
        w = _measure_label(ntype, label)
        cache[key] = w
        return w
    total = sum(_calc_width(c, cache) for c in children)
    cache[key] = total
    return total


def _layout(node, x_offset, depth, positions, width_cache):
    w_units = _calc_width(node, width_cache)
    w_px = w_units + (len(_collect_children(node)) - 1) * H_SPACING if _collect_children(node) else w_units
    x_center = x_offset + w_px / 2
    y = PADDING + depth * (NODE_H + V_SPACING)

    ntype, label = _node_label(node)
    node_w = _measure_label(ntype, label)
    positions.append({
        'node': node,
        'x': x_center,
        'y': y,
        'w': node_w,
        'h': NODE_H,
    })

    children = _collect_children(node)
    cx = x_offset
    for child in children:
        cw = _calc_width(child, width_cache)
        _layout(child, cx, depth + 1, positions, width_cache)
        cx += cw + H_SPACING

    return positions


def _esc(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


def _build_legend():
    items = []
    for ntype, style in sorted(NODE_STYLES.items()):
        items.append(
            f'<rect x="{PADDING}" y="{y}" width="14" height="14" rx="3" '
            f'fill="{style["fill"]}" stroke="{style["border"]}" stroke-width="0.5"/>'
            f'<text x="{PADDING + 20}" y="{y + 11}" font-size="10" fill="#7F8C8D" '
            f'font-family="{FONT}">{ntype}</text>'
        )
    return items


def ast_to_svg(ast_dict):
    if not ast_dict:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" '
                'viewBox="0 0 300 120" style="background:#FAFBFC;">'
                '<text x="150" y="60" text-anchor="middle" font-family="sans-serif" '
                'font-size="14" fill="#999">(AST vacio)</text></svg>')

    width_cache = {}
    positions = []
    _layout(ast_dict, PADDING, 0, positions, width_cache)

    if not positions:
        return '<svg/>'

    max_x = max(p['x'] + p['w'] / 2 for p in positions) + PADDING + LEGEND_W
    max_y = max(p['y'] + p['h'] for p in positions) + PADDING + 20
    svg_w = max(int(max_x), 600)
    svg_h = max(int(max_y), 300)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" '
        f'style="background:#FAFBFC;font-family:{FONT},sans-serif;">',

        '<defs>',
        '  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">'
        '    <feDropShadow dx="1" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.13"/>'
        '  </filter>',
        '  <filter id="shadow-light" x="-20%" y="-20%" width="140%" height="140%">'
        '    <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#000" flood-opacity="0.08"/>'
        '  </filter>',
        '  <marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" '
        '    markerWidth="6" markerHeight="6" orient="auto">'
        '    <path d="M0,1 L10,6 L0,11 Z" fill="#8E99A4"/>'
        '  </marker>',
        '  <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">'
        '    <stop offset="0%" stop-color="#F8F9FA"/>'
        '    <stop offset="100%" stop-color="#EEF1F5"/>'
        '  </linearGradient>',
        '  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">'
        '    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E8ECF0" stroke-width="0.5"/>'
        '  </pattern>',
        '</defs>',

        f'<rect width="100%" height="100%" fill="url(#bg-grad)"/>',
        f'<rect width="100%" height="100%" fill="url(#grid)"/>',
    ]

    pos_map = {id(p['node']): p for p in positions}

    for p in positions:
        node = p['node']
        nx, ny = p['x'], p['y'] + p['h']
        children = _collect_children(node)
        for child in children:
            cp = pos_map.get(id(child))
            if cp:
                cx, cy = cp['x'], cp['y']
                mid_y = ny + (cy - ny) * 0.45
                ctrl1_y = ny + (cy - ny) * 0.2
                ctrl2_y = ny + (cy - ny) * 0.8
                lines.append(
                    f'<path d="M{nx:.0f},{ny:.0f} C{nx:.0f},{ctrl1_y:.0f} '
                    f'{cx:.0f},{ctrl2_y:.0f} {cx:.0f},{cy:.0f}" '
                    f'fill="none" stroke="#BDC3C7" stroke-width="1.8" '
                    f'stroke-linecap="round" marker-end="url(#arrow)"/>'
                )

    for p in positions:
        node = p['node']
        nx, ny = p['x'], p['y']
        ntype, label = _node_label(node)
        style = NODE_STYLES.get(ntype, DEFAULT_STYLE)
        fill = style['fill']
        text_color = style['text']
        border = style['border']
        x0 = nx - p['w'] / 2

        y_offset_up = ny + 16
        y_offset_down = ny + 32

        lines.append(
            f'<rect x="{x0 + 2:.0f}" y="{ny + 2:.0f}" '
            f'width="{p["w"]}" height="{p["h"]}" rx="7" fill="rgba(0,0,0,0.10)"/>'
        )

        lines.append(
            f'<rect x="{x0:.0f}" y="{ny:.0f}" '
            f'width="{p["w"]}" height="{p["h"]}" rx="7" '
            f'fill="{fill}" stroke="{border}" stroke-width="1.2" '
            f'filter="url(#shadow)"/>'
        )

        lines.append(
            f'<text x="{nx:.0f}" y="{y_offset_up:.0f}" text-anchor="middle" '
            f'fill="{text_color}" font-size="11" font-weight="700" '
            f'font-family="{FONT_MONO}">{_esc(ntype)}</text>'
        )

        label_text = _esc(label) if label else ''
        if label_text and label_text != _esc(ntype):
            lines.append(
                f'<text x="{nx:.0f}" y="{y_offset_down:.0f}" text-anchor="middle" '
                f'fill="{text_color}" font-size="9" font-weight="400" '
                f'font-family="{FONT_MONO}" opacity="0.85">{label_text}</text>'
            )

    legend_x = max_x - LEGEND_W + 10
    legend_y = PADDING
    lines.append(
        f'<rect x="{legend_x - 10:.0f}" y="{legend_y - 10:.0f}" '
        f'width="{LEGEND_W}" height="{len(NODE_STYLES) * 22 + 30}" rx="6" '
        f'fill="#FFFFFF" stroke="#DDE2E6" stroke-width="1" filter="url(#shadow-light)"/>'
    )
    lines.append(
        f'<text x="{legend_x:.0f}" y="{legend_y + 4:.0f}" '
        f'font-size="10" font-weight="700" fill="#4A5568" font-family="{FONT}">'
        f'Leyenda</text>'
    )

    i = 0
    for ntype, nstyle in sorted(NODE_STYLES.items()):
        ly = legend_y + 22 + i * 20
        lines.append(
            f'<rect x="{legend_x:.0f}" y="{ly:.0f}" width="12" height="12" rx="2" '
            f'fill="{nstyle["fill"]}" stroke="{nstyle["border"]}" stroke-width="0.5"/>'
        )
        lines.append(
            f'<text x="{legend_x + 18:.0f}" y="{ly + 10:.0f}" '
            f'font-size="9" fill="#5A6872" font-family="{FONT_MONO}">{ntype}</text>'
        )
        i += 1

    lines.append('</svg>')
    return '\n'.join(lines)
