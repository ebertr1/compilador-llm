import React, { useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';

export default function CodeEditor({ value, onChange, onCompile, loading, errorLines }) {
  const editorRef = useRef(null);

  const handleMount = useCallback((editor) => {
    editorRef.current = editor;
  }, []);

  React.useEffect(() => {
    const ed = editorRef.current;
    if (!ed) return;
    const model = ed.getModel();
    if (!model) return;

    const lines = new Set(errorLines || []);
    const decorations = [];
    for (let l = 1; l <= model.getLineCount(); l++) {
      if (lines.has(l)) {
        decorations.push({
          range: new window.monaco.Range(l, 1, l, 1),
          options: {
            isWholeLine: true,
            glyphMarginClassName: 'error-glyph',
            glyphMarginHoverMessage: { value: 'Error de compilación' },
            linesDecorationsClassName: 'error-line-decoration',
          },
        });
      }
    }
    ed.deltaDecorations([], decorations);
  }, [errorLines, value]);

  const handleFormat = () => {
    if (!editorRef.current) return;
    editorRef.current.getAction('editor.action.formatDocument')?.run();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{
        padding: '8px 16px', background: '#181825',
        borderBottom: '1px solid #313244',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <span style={{ fontSize: 13, color: '#a6adc8' }}>Código fuente</span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={handleFormat}
            style={{
              padding: '8px 14px', background: '#45475a',
              border: 'none', borderRadius: 6, color: '#cdd6f4',
              cursor: 'pointer', fontWeight: 500, fontSize: 13,
            }}
          >
            Formatear
          </button>
          <button
            onClick={onCompile}
            disabled={loading}
            style={{
              padding: '8px 20px', background: loading ? '#585b70' : '#a6e3a1',
              border: 'none', borderRadius: 6, color: '#1e1e2e',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 600, fontSize: 14,
            }}
          >
            {loading ? 'Compilando...' : 'Compilar'}
          </button>
        </div>
      </div>
      <div style={{ flex: 1 }}>
        <style>{`
          .error-glyph {
            background: #f38ba8;
            width: 6px !important;
            height: 6px !important;
            border-radius: 50%;
            margin-left: 8px;
            margin-top: 8px;
          }
          .error-line-decoration {
            background: rgba(243, 139, 168, 0.1);
            border-left: 3px solid #f38ba8;
          }
        `}</style>
        <Editor
          height="100%"
          defaultLanguage="plaintext"
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange(v || '')}
          onMount={handleMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: 'JetBrains Mono, monospace',
            lineNumbers: 'on',
            renderWhitespace: 'selection',
            tabSize: 4,
            glyphMargin: true,
          }}
        />
      </div>
    </div>
  );
}
