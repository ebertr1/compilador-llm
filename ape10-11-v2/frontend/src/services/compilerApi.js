const API_BASE = '/api';
const WS_URL = `ws://${window.location.hostname}:8083/ws/compile`;

export async function compileRest(code) {
  const res = await fetch(`${API_BASE}/compile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function compileWs(code, onPhase, onResult, onExplanation, onError) {
  const ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    ws.send(JSON.stringify({ code }));
  };
  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.phase) {
        onPhase?.(msg.phase, msg.status);
      } else if (msg.type === 'result') {
        onResult?.(msg.data);
      } else if (msg.type === 'explanation') {
        onExplanation?.(msg.data);
      } else if (msg.type === 'error') {
        onError?.(msg.message);
        ws.close();
      }
    } catch {
      onError?.('Error parseando respuesta');
    }
  };
  ws.onerror = () => onError?.('Error de conexión WebSocket');
  return ws;
}
