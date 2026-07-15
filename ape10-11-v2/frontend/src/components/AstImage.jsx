import React, { useMemo, useRef, useState, useCallback } from 'react';

const NODE_W = 120;
const NODE_H = 32;
const H_GAP = 16;
const V_GAP = 50;

function isObject(v) { return v && typeof v === 'object'; }

function collectChildren(obj) {
  const kids = [];
  for (const [k, v] of Object.entries(obj)) {
    if (k === 'type' || k === 'line') continue;
    if (Array.isArray(v)) {
      v.forEach(item => { if (isObject(item)) kids.push(item); });
    } else if (isObject(v)) {
      kids.push(v);
    }
  }
  return kids;
}

function nodeType(obj) {
  return obj && typeof obj === 'object' ? (obj.type || '?') : typeof obj;
}

const COLORS = {
  Program: '#89b4fa', VarDecl: '#a6e3a1', Assign: '#f9e2af',
  IfStmt: '#cba6f7', WhileStmt: '#fab387', ForStmt: '#f38ba8',
  PrintStmt: '#89dceb', Block: '#6c7086', BinOp: '#74c7ec',
  UnaryOp: '#94e2d5', Literal: '#f5c2e7', VarRef: '#b4befe',
  EnetroDef: '#f5c2e7', EnetroField: '#f9e2af', EnetroAccess: '#fab387',
};
function color(type) { return COLORS[type] || '#a6adc8'; }

function layout(node, depth = 0) {
  if (!node || typeof node !== 'object')
    return { w: NODE_W, h: NODE_H, nodes: [] };

  const children = collectChildren(node);
  if (children.length === 0) {
    return {
      w: NODE_W, h: NODE_H,
      nodes: [{ node, x: NODE_W / 2, y: depth * (NODE_H + V_GAP) + NODE_H / 2, depth }],
    };
  }

  const layouts = children.map(c => layout(c, depth + 1));
  const totalW = layouts.reduce((s, l) => s + l.w + H_GAP, 0) - H_GAP;
  const w = Math.max(NODE_W, totalW);
  const maxH = Math.max(...layouts.map(l => l.h));
  const h = maxH + NODE_H + V_GAP;

  const allNodes = [];
  let offset = (w - totalW) / 2;
  for (const l of layouts) {
    for (const n of l.nodes) allNodes.push({ ...n, x: n.x + offset });
    offset += l.w + H_GAP;
  }

  const cx = w / 2;
  allNodes.push({ node, x: cx, y: depth * (NODE_H + V_GAP) + NODE_H / 2, depth });
  return { w, h, nodes: allNodes };
}

export default function AstImage({ data }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const panStart = useRef({ x: 0, y: 0 });

  const laid = useMemo(() => {
    if (!data || typeof data !== 'object') return null;
    return layout(data);
  }, [data]);

  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(z => Math.max(0.2, Math.min(5, z * delta)));
  }, []);

  const handleMouseDown = useCallback((e) => {
    if (e.button === 0) {
      setDragging(true);
      dragStart.current = { x: e.clientX, y: e.clientY };
      panStart.current = { ...pan };
    }
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (!dragging) return;
    const dx = e.clientX - dragStart.current.x;
    const dy = e.clientY - dragStart.current.y;
    setPan({ x: panStart.current.x + dx, y: panStart.current.y + dy });
  }, [dragging]);

  const handleMouseUp = useCallback(() => setDragging(false), []);

  const fitToWidth = useCallback(() => {
    if (!containerRef.current || !laid) return;
    const cw = containerRef.current.clientWidth - 40;
    const scale = cw / laid.w;
    setZoom(Math.min(scale, 2.5));
    setPan({ x: 0, y: 0 });
  }, [laid]);

  if (!laid || laid.nodes.length === 0) return null;

  const W = laid.w + 40;
  const H = laid.h + 60;
  const padX = 20, padTop = 30;

  const nodeMap = {};
  laid.nodes.forEach((n, i) => { nodeMap[i] = n; });
  const parentIdx = laid.nodes.length - 1;

  const lines = laid.nodes.flatMap((n, i) => {
    if (i === parentIdx) return [];
    const children = laid.nodes.filter((c, j) => j !== parentIdx && c.depth === n.depth + 1);
    return children.map(child => (
      <line
        key={`l-${i}-${child.x}`}
        x1={n.x + padX} y1={padTop + n.y + NODE_H / 2}
        x2={child.x + padX} y2={padTop + child.y - NODE_H / 2}
        stroke="#585b70" strokeWidth="1.5"
      />
    ));
  });

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
        <button onClick={fitToWidth} style={{
          padding: '4px 10px', background: '#45475a', border: 'none',
          borderRadius: 4, color: '#cdd6f4', cursor: 'pointer', fontSize: 12,
        }}>
          Ajustar al ancho
        </button>
        <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} style={{
          padding: '4px 10px', background: '#313244', border: 'none',
          borderRadius: 4, color: '#cdd6f4', cursor: 'pointer', fontSize: 12,
        }}>
          Reset
        </button>
        <span style={{ fontSize: 11, color: '#6c7086' }}>{Math.round(zoom * 100)}%</span>
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            if (!svgRef.current) return;
            const svg = svgRef.current;
            const clone = svg.cloneNode(true);
            clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            const blob = new Blob([new XMLSerializer().serializeToString(clone)], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'ast.svg'; a.click();
            URL.revokeObjectURL(url);
          }}
          style={{ marginLeft: 'auto', color: '#89b4fa', fontSize: 12 }}
        >
          Descargar SVG
        </a>
      </div>
      <div
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          background: '#11111b', borderRadius: 8, overflow: 'hidden',
          border: '1px solid #313244', cursor: dragging ? 'grabbing' : 'grab',
          height: 450, position: 'relative',
        }}
      >
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          style={{
            width: '100%', height: '100%',
            transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
            transformOrigin: '0 0',
          }}
        >
          <defs>
            <filter id="shadow">
              <feDropShadow dx="0" dy="1" stdDeviation="1" floodColor="#000" floodOpacity="0.4" />
            </filter>
          </defs>
          {lines}
          {laid.nodes.map((n, i) => {
            const px = n.x - NODE_W / 2 + padX;
            const py = padTop + n.y - NODE_H / 2;
            return (
              <g key={i}>
                <rect x={px} y={py} width={NODE_W} height={NODE_H}
                  rx={6} ry={6} fill={color(nodeType(n.node))} filter="url(#shadow)" />
                <text x={px + NODE_W / 2} y={py + NODE_H / 2}
                  textAnchor="middle" dominantBaseline="central"
                  fill="#11111b" fontWeight="bold" fontSize={11} fontFamily="monospace">
                  {nodeType(n.node)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
