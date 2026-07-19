import http from 'http';
import 'dotenv/config';
import app from './app';
import { logger } from './config/logger';
import { initWebSocket } from './modules/websocket/websocket.gateway';

const PORT = parseInt(process.env.PORT ?? '3000', 10);

const server = http.createServer(app);
initWebSocket(server);

server.listen(PORT, () => {
  logger.info('MS1 Core API started', { port: PORT, env: process.env.NODE_ENV ?? 'development' });
});
