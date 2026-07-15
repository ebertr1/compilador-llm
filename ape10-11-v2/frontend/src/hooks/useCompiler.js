import { useState, useCallback } from 'react';
import { compileRest } from '../services/compilerApi';

export function useCompiler() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [phases, setPhases] = useState({});

  const compile = useCallback(async (code) => {
    setLoading(true);
    setError(null);
    setPhases({});
    try {
      const data = await compileRest(code);
      setResult(data);
      setPhases({
        lexical: 'done',
        syntactic: 'done',
        semantic: 'done',
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setPhases({});
  }, []);

  return { result, loading, error, phases, compile, reset };
}
