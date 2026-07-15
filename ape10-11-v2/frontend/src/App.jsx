import React from 'react';
import { useCompiler } from './hooks/useCompiler';
import CodeEditor from './components/CodeEditor';
import ResultPanel from './components/ResultPanel';

export default function App() {
  const { result, loading, error, phases, compile, reset } = useCompiler();
  const [code, setCode] = React.useState('');

  const errorLines = React.useMemo(() => {
    if (!result?.errors) return [];
    return result.errors.map(e => e.line).filter(l => l > 0);
  }, [result]);

  const handleNavigate = React.useCallback((line) => {
    setCode(prev => prev);
  }, []);

  const examples = [
    { name: 'Código correcto', file: 'correct_sp.txt' },
    { name: 'Código con errores', file: 'errors_sp.txt' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{
        padding: '12px 20px', background: '#181825',
        borderBottom: '1px solid #313244', display: 'flex',
        alignItems: 'center', gap: 16,
      }}>
        <h1 style={{ margin: 0, fontSize: 18, color: '#cba6f7' }}>
          Compilador APE10-11 v2
        </h1>
        <span style={{ fontSize: 12, color: '#6c7086' }}>Java + React + IA</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          {examples.map((ex) => (
            <button key={ex.name} onClick={async () => {
              try {
                const res = await fetch(`/api/examples/${ex.file}`);
                if (res.ok) {
                  const data = await res.json();
                  setCode(data.code || '');
                  reset();
                }
              } catch {}
            }} style={{
              padding: '6px 12px', background: '#313244', border: 'none',
              borderRadius: 6, color: '#cdd6f4', cursor: 'pointer', fontSize: 13,
            }}>{ex.name}</button>
          ))}
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <CodeEditor
            value={code}
            onChange={setCode}
            onCompile={() => compile(code)}
            loading={loading}
            errorLines={errorLines}
          />
        </div>
        <div style={{ width: 1, background: '#313244' }} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
          <ResultPanel result={result} loading={loading} error={error} phases={phases} />
        </div>
      </div>
    </div>
  );
}
