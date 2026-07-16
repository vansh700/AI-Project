import { Request, Response, NextFunction } from 'express';
import { prisma } from '../../config/prisma.client';
import { logger } from '../../config/logger';

const ALLOWED_STATUSES = ['COMPLETED', 'FAILED', 'RUNNING'] as const;
type JobStatus = typeof ALLOWED_STATUSES[number];

export async function handleJobComplete(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const secret = req.headers['x-webhook-secret'];
    if (secret !== process.env.WEBHOOK_SECRET) {
      res.status(401).json({ status: 'error', message: 'Invalid webhook secret' });
      return;
    }

    const { jobId, status, error } = req.body as { jobId: string; status: string; error?: string };

    if (!jobId || !status) {
      res.status(400).json({ status: 'error', message: 'jobId and status are required' });
      return;
    }

    if (!ALLOWED_STATUSES.includes(status as JobStatus)) {
      res.status(400).json({ status: 'error', message: `Invalid status: ${status}` });
      return;
    }

    const job = await prisma.analysisJob.update({
      where: { id: jobId },
      data: { status },
    });

    logger.info('Job status updated via webhook', { jobId, status, error });

    res.status(200).json({ job });
  } catch (err) {
    next(err);
  }
}
