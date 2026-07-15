import React, { useState } from 'react';
import AstTreeView from './AstTreeView';
import AstImage from './AstImage';

const ERROR_COLORS = {
  lexical: '#f38ba8',
  syntactic: '#fab387',
  semantic: '#cba6f7',
};
const ERROR_LABELS = {
  lexical: 'Léxico',
  syntactic: 'Sintáctico',
  semantic: 'Semántico',
};
const ERROR_BG = {
  lexical: '#3a1e1e',
  syntactic: '#3a2a1e',
  semantic: '#2a1e3a',
};
const ERROR_BORDER = {
  lexical: '#452020',
  syntactic: '#453020',
  semantic: '#302045',
};

export default function ResultPanel({ result, loading, error, phases, onNavigate }) {
  const [astView, setAstView] = useState('tree');
  const [expandedErrors, setExpandedErrors] = useState(new Set());

  const toggleError = (i) => {
    setExpandedErrors(prev => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i); else next.add(i);
      return next;
    });
  };

  if (loading) {
    return (
      <div style={{ padding: 20 }}>
        <h3 style={{ color: '#a6adc8', marginTop: 0 }}>Compilando...</h3>
        {['lexical', 'syntactic', 'semantic'].map((p) => (
          <div key={p} style={{ margin: '8px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              width: 10, height: 10, borderRadius: '50%',
              background: phases[p] ? '#a6e3a1' : '#585b70',
              display: 'inline-block',
            }} />
            <span style={{ color: '#cdd6f4', fontSize: 13 }}>
              {p === 'lexical' ? 'Análisis Léxico' :
               p === 'syntactic' ? 'Análisis Sintáctico' :
               'Análisis Semántico'}
            </span>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 20 }}>
        <h3 style={{ color: '#f38ba8', marginTop: 0 }}>Error</h3>
        <p style={{ color: '#cdd6f4' }}>{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{
        padding: 20, display: 'flex', alignItems: 'center',
        justifyContent: 'center', height: '100%', color: '#6c7086',
      }}>
        Escribe código y presiona Compilar
      </div>
    );
  }

  const hasErrors = result.errors && result.errors.length > 0;
  const hasTokens = result.tokens && result.tokens.length > 0;
  const hasTree = result.tree !== undefined && result.tree !== null;
  const hasSymbols = result.symbolTable && Object.keys(result.symbolTable).length > 0;
  const hasErrorExplanations = result.errorExplanations && result.errorExplanations.length > 0;

  return (
    <div style={{ padding: 20, overflow: 'auto' }}>
      <div style={{
        padding: '10px 16px', borderRadius: 8, marginBottom: 16,
        background: hasErrors ? '#3a1e1e' : '#1e3a2f',
        border: `1px solid ${hasErrors ? '#f38ba8' : '#a6e3a1'}`,
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <span style={{
          width: 8, height: 8, borderRadius: '50%',
          background: hasErrors ? '#f38ba8' : '#a6e3a1',
          display: 'inline-block', flexShrink: 0,
        }} />
        <strong style={{ color: hasErrors ? '#f38ba8' : '#a6e3a1', fontSize: 14 }}>
          {hasErrors ? 'Errores de compilación' : 'Compilación exitosa'}
        </strong>
        {hasErrors && (
          <span style={{ color: '#fab387', fontSize: 12, marginLeft: 'auto' }}>
            {result.errors.length} error{result.errors.length > 1 ? 'es' : ''}
          </span>
        )}
      </div>

      {hasErrors && (
        <section style={{ marginBottom: 16 }}>
          <h4 style={{
            color: '#f38ba8', margin: '0 0 10px', fontSize: 14,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            Errores
          </h4>
          {result.errors.map((err, i) => {
            const etype = (err.type || 'unknown').toLowerCase();
            const ec = ERROR_COLORS[etype] || '#ffd700';
            const el = ERROR_LABELS[etype] || err.type;
            const eb = ERROR_BG[etype] || '#2a2a1e';
            const ebo = ERROR_BORDER[etype] || '#353520';
            const isExpanded = expandedErrors.has(i);
            const iaText = hasErrorExplanations ? result.errorExplanations[i] : null;
            return (
              <div key={i} style={{
                padding: '10px 12px', background: eb,
                borderRadius: 6, marginBottom: 6,
                border: `1px solid ${ebo}`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span style={{
                    display: 'inline-block', padding: '1px 8px', borderRadius: 3,
                    background: ec, color: '#11111b', fontWeight: 700, fontSize: 10,
                    textTransform: 'uppercase', fontFamily: 'monospace',
                  }}>
                    {el}
                  </span>
                  <span
                    onClick={() => onNavigate?.(err.line)}
                    style={{ color: '#6c7086', fontSize: 11, cursor: onNavigate ? 'pointer' : 'default', textDecoration: onNavigate ? 'underline dotted' : 'none' }}
                  >
                    Línea {err.line}
                  </span>
                  {iaText && (
                    <span
                      onClick={() => toggleError(i)}
                      style={{ marginLeft: 'auto', color: '#cba6f7', fontSize: 11, cursor: 'pointer', userSelect: 'none' }}
                    >
                      {isExpanded ? '▲ IA' : '▼ IA'}
                    </span>
                  )}
                </div>
                <div style={{ color: '#cdd6f4', fontSize: 13, marginLeft: 2 }}>
                  {err.message}
                </div>
                {iaText && isExpanded && (
                  <div style={{
                    marginTop: 8, padding: '8px 10px', background: '#1e1e3a',
                    borderRadius: 4, fontSize: 12, color: '#cdd6f4',
                    lineHeight: 1.5, whiteSpace: 'pre-wrap',
                    border: '1px solid #313244',
                  }}>
                    <span style={{ color: '#cba6f7', fontWeight: 600, fontSize: 10, textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>
                      IA Explicación
                    </span>
                    {iaText}
                  </div>
                )}
              </div>
            );
          })}
        </section>
      )}

      {result.llmExplanation && (
        <section style={{ marginBottom: 16 }}>
          <h4 style={{ color: '#cba6f7', margin: '0 0 8px', fontSize: 14 }}>
            IA Explicación
          </h4>
          <div style={{
            padding: 12, background: '#1e1e3a', borderRadius: 6,
            fontSize: 13, color: '#cdd6f4', lineHeight: 1.5,
            whiteSpace: 'pre-wrap',
          }}>
            {result.llmExplanation}
          </div>
        </section>
      )}

      {hasTokens && (
        <section style={{ marginBottom: 16 }}>
          <h4 style={{
            color: '#89dceb', margin: '0 0 8px', fontSize: 14,
          }}>
            Tokens ({result.tokens.length})
          </h4>
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: 4,
            background: '#181825', padding: 8, borderRadius: 6,
            maxHeight: 160, overflow: 'auto',
          }}>
            {result.tokens.map((t, i) => (
              <span key={i} style={{
                padding: '2px 8px', background: '#313244',
                borderRadius: 4, fontSize: 12, color: '#74c7ec',
                fontFamily: 'monospace', whiteSpace: 'nowrap',
              }}>
                <span style={{ color: '#a6e3a1' }}>{t.type}</span>
                {' '}
                <span style={{ color: '#f5c2e7' }}>'{t.value}'</span>
                <span style={{ color: '#6c7086' }}> L{t.line}</span>
              </span>
            ))}
          </div>
        </section>
      )}

      {hasTree && (
        <section style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <h4 style={{ color: '#f9e2af', margin: 0, fontSize: 14 }}>AST</h4>
            <div style={{ display: 'flex', gap: 4, background: '#181825', borderRadius: 4, padding: 2 }}>
              <button
                onClick={() => setAstView('tree')}
                style={{
                  padding: '2px 10px', border: 'none', borderRadius: 3,
                  background: astView === 'tree' ? '#45475a' : 'transparent',
                  color: '#cdd6f4', cursor: 'pointer', fontSize: 11,
                }}
              >
                Árbol
              </button>
              <button
                onClick={() => setAstView('image')}
                style={{
                  padding: '2px 10px', border: 'none', borderRadius: 3,
                  background: astView === 'image' ? '#45475a' : 'transparent',
                  color: '#cdd6f4', cursor: 'pointer', fontSize: 11,
                }}
              >
                Imagen
              </button>
            </div>
          </div>
          {astView === 'tree' ? (
            <div style={{
              background: '#181825', padding: 12, borderRadius: 6,
              fontFamily: 'monospace', fontSize: 12, overflow: 'auto',
              maxHeight: 400, color: '#cdd6f4',
            }}>
              <AstTreeView data={result.tree} />
            </div>
          ) : (
            <AstImage data={result.tree} />
          )}
        </section>
      )}

      {hasSymbols && (
        <section style={{ marginBottom: 16 }}>
          <h4 style={{
            color: '#94e2d5', margin: '0 0 8px', fontSize: 14,
          }}>
            Tabla de Símbolos
          </h4>
          <div style={{ overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: '#313244' }}>
                  <th style={{ padding: '6px 12px', textAlign: 'left', color: '#a6adc8' }}>Variable</th>
                  <th style={{ padding: '6px 12px', textAlign: 'left', color: '#a6adc8' }}>Tipo</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.symbolTable).map(([name, type]) => (
                  <tr key={name} style={{ borderBottom: '1px solid #313244' }}>
                    <td style={{ padding: '4px 12px', color: '#f5c2e7', fontFamily: 'monospace' }}>{name}</td>
                    <td style={{ padding: '4px 12px', color: '#89b4fa', fontFamily: 'monospace' }}>{type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
