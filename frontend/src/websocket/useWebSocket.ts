import { useEffect, useRef, useState, useCallback } from 'react';
import { SystemSnapshot, WsMessage, DemoEntry } from '../types';

interface UseWebSocketReturn {
  snapshot: SystemSnapshot | null;
  demos: DemoEntry[];
  connected: boolean;
  loadResult: { success: boolean; message: string } | null;
  sendMessage: (msg: object) => void;
  loadProgram: (source: string) => void;
  step: (count?: number) => void;
  run: () => void;
  reset: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const [snapshot, setSnapshot] = useState<SystemSnapshot | null>(null);
  const [demos, setDemos] = useState<DemoEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const [loadResult, setLoadResult] = useState<{ success: boolean; message: string } | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const sendMessage = useCallback((msg: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const loadProgram = useCallback((source: string) => {
    sendMessage({ type: 'load', source });
  }, [sendMessage]);

  const step = useCallback((count = 1) => {
    sendMessage({ type: 'step', count });
  }, [sendMessage]);

  const run = useCallback(() => {
    sendMessage({ type: 'run' });
  }, [sendMessage]);

  const reset = useCallback(() => {
    sendMessage({ type: 'reset' });
  }, [sendMessage]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;

    function connect() {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        // Request demos immediately on connect
        ws.send(JSON.stringify({ type: 'get_default_demo' }));
      };

      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 2000);
      };

      ws.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          switch (msg.type) {
            case 'snapshot':
              setSnapshot(msg.data);
              break;
            case 'status':
              setConnected(msg.data.connected);
              break;
            case 'load_result':
              setLoadResult(msg.data);
              break;
            case 'demos':
              setDemos(msg.data);
              break;
          }
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };
    }

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, []);

  return { snapshot, demos, connected, loadResult, sendMessage, loadProgram, step, run, reset };
}
