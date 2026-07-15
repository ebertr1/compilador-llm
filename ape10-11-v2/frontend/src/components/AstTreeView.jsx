import React, { useState } from 'react';

const NODE_COLORS = {
  Program: '#89b4fa',
  VarDecl: '#a6e3a1',
  Assign: '#f9e2af',
  IfStmt: '#cba6f7',
  WhileStmt: '#fab387',
  ForStmt: '#f38ba8',
  PrintStmt: '#89dceb',
  Block: '#6c7086',
  BinOp: '#74c7ec',
  UnaryOp: '#94e2d5',
  Literal: '#f5c2e7',
  VarRef: '#b4befe',
  EnetroRef: '#a6adc8',
  EnetroDef: '#f5c2e7',
  EnetroField: '#f9e2af',
  EnetroAccess: '#fab387',
};

function getColor(type) {
  return NODE_COLORS[type] || '#a6adc8';
}

function isLeaf(val) {
  return val === null || val === undefined || typeof val !== 'object';
}

export default function AstTreeView({ data, depth = 0 }) {
  if (!data || typeof data !== 'object') {
    return <span style={{ color: '#74c7ec' }}>{String(data)}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <div style={{ marginLeft: depth * 20 }}>
        {data.map((item, i) => (
          <AstTreeView key={i} data={item} depth={depth} />
        ))}
      </div>
    );
  }

  const type = data.type;
  const entries = Object.entries(data).filter(
    ([k, v]) => k !== 'type' && !isLeaf(v) && v !== null
  );
  const attrs = Object.entries(data).filter(
    ([k, v]) => k !== 'type' && isLeaf(v)
  );

  return (
    <div style={{ marginLeft: depth * 20, marginTop: 2, marginBottom: 2 }}>
      <NodeHeader type={type} attrs={attrs} depth={depth} />
      {entries.length > 0 && (
        <div style={{ borderLeft: '1px solid #45475a', marginLeft: 8, paddingLeft: 8 }}>
          {entries.map(([key, val]) => (
            <Section key={key} label={key}>
              {Array.isArray(val) ? (
                val.map((item, i) => (
                  <AstTreeView key={i} data={item} depth={1} />
                ))
              ) : (
                <AstTreeView data={val} depth={1} />
              )}
            </Section>
          ))}
        </div>
      )}
    </div>
  );
}

function NodeHeader({ type, attrs, depth }) {
  const [open, setOpen] = useState(depth < 2);
  const hasDetails = attrs.length > 0;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
      <span style={{
        display: 'inline-block', padding: '2px 8px', borderRadius: 4,
        background: getColor(type), color: '#11111b',
        fontWeight: 700, fontSize: 12, fontFamily: 'monospace',
      }}>
        {type}
      </span>
      {hasDetails && (
        <span
          onClick={() => setOpen(!open)}
          style={{ cursor: 'pointer', color: '#6c7086', fontSize: 11, userSelect: 'none' }}
        >
          {open ? '▲' : '▼'}
        </span>
      )}
      {open && attrs.map(([k, v]) => (
        <span key={k} style={{
          background: '#313244', padding: '1px 6px', borderRadius: 3,
          fontSize: 11, color: '#a6adc8', fontFamily: 'monospace',
        }}>
          {k}=<span style={{ color: '#f5c2e7' }}>{String(v)}</span>
        </span>
      ))}
    </div>
  );
}

function Section({ label, children }) {
  return (
    <div style={{ marginTop: 2, marginBottom: 2 }}>
      <span style={{
        color: '#585b70', fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
        letterSpacing: '0.5px', marginLeft: 4,
      }}>
        {label}
      </span>
      {children}
    </div>
  );
}
