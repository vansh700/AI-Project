import { WebSocketServer, WebSocket } from 'ws';
import jwt from 'jsonwebtoken';
import { Server } from 'http';
import { logger } from '../../config/logger';

interface JwtPayload {
  userId: string;
}

const clients = new Map<string, Set<WebSocket>>();

export function initWebSocket(server: Server): WebSocketServer {
  const wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (socket, req) => {
    const url = new URL(req.url ?? '', `http://${req.headers.host}`);
    const token = url.searchParams.get('token');

    if (!token) {
      socket.close(4001, 'Missing token');
      return;
    }

    let userId: string;
    try {
      const payload = jwt.verify(token, process.env.JWT_SECRET as string) as JwtPayload;
      userId = payload.userId;
    } catch {
      socket.close(4002, 'Invalid token');
      return;
    }

    if (!clients.has(userId)) {
      clients.set(userId, new Set());
    }
    clients.get(userId)!.add(socket);

    socket.on('close', () => {
      clients.get(userId)?.delete(socket);
      if (clients.get(userId)?.size === 0) {
        clients.delete(userId);
      }
    });

    socket.send(JSON.stringify({ event: 'connected', userId }));
    logger.info('WebSocket client connected', { userId });
  });

  logger.info('WebSocket server initialised on /ws');
  return wss;
}

export function emitJobUpdate(userId: string, payload: unknown): void {
  const sockets = clients.get(userId);
  if (!sockets?.size) {
    return;
  }

  const message = JSON.stringify(payload);
  for (const socket of sockets) {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  }
}
