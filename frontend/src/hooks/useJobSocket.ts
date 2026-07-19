import { useEffect, useRef, useCallback } from 'react';
import { getToken } from '../api/client';
import type { AnalysisJob } from '../types/api.types';

interface JobUpdateMessage {
  event: string;
  job: AnalysisJob;
}

export function useJobSocket(onJobUpdate: (job: AnalysisJob) => void): void {
  const callbackRef = useRef(onJobUpdate);
  callbackRef.current = onJobUpdate;

  const connect = useCallback(() => {
    const token = getToken();
    if (!token) return null;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const socket = new WebSocket(`${protocol}//${host}/ws?token=${encodeURIComponent(token)}`);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as JobUpdateMessage;
        if (data.event === 'job_updated' && data.job) {
          callbackRef.current(data.job);
        }
      } catch {
        // ignore malformed messages
      }
    };

    socket.onclose = () => {
      setTimeout(() => connect(), 3000);
    };

    return socket;
  }, []);

  useEffect(() => {
    const socket = connect();
    return () => socket?.close();
  }, [connect]);
}
