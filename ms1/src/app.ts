import express, { Application, Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { healthRoutes } from './health/health.routes';
import { authRoutes } from './modules/auth/auth.routes';
import { projectRoutes } from './modules/project/project.routes';
import { analysisRoutes } from './modules/analysis/analysis.routes';
import { webhookRoutes } from './modules/webhook/webhook.routes';
import { logger } from './config/logger';

const app: Application = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/health', healthRoutes);
app.use('/auth', authRoutes);
app.use('/projects', projectRoutes);
app.use('/projects/:id/analysis', analysisRoutes);
app.use('/webhooks', webhookRoutes);

app.use((_req: Request, res: Response) => {
  res.status(404).json({ status: 'error', message: 'Route not found' });
});

// Express identifies error handlers by their 4-parameter signature — _next must be present.
app.use((err: Error & { statusCode?: number }, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof ZodError) {
    res.status(400).json({
      status: 'error',
      message: 'Validation failed',
      errors: err.errors.map((e) => ({ field: e.path.join('.'), message: e.message })),
    });
    return;
  }

  if (err.name === 'MulterError' || (err as any).code === 'LIMIT_FILE_SIZE') {
    const message = (err as any).code === 'LIMIT_FILE_SIZE' ? 'File too large. Max size allowed is 100MB.' : err.message;
    res.status(400).json({ status: 'error', message });
    return;
  }

  if (err.statusCode) {
    res.status(err.statusCode).json({ status: 'error', message: err.message });
    return;
  }

  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({ status: 'error', message: 'Internal server error' });
});

export default app;
