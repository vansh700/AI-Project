import { Request, Response, NextFunction } from 'express';
import { prisma } from '../../config/prisma.client';
import { logger } from '../../config/logger';
import { buildReportSummary } from '../report/report.service';
import { emitJobUpdate } from '../websocket/websocket.gateway';

const ALLOWED_STATUSES = ['COMPLETED', 'FAILED', 'RUNNING'] as const;
type JobStatus = typeof ALLOWED_STATUSES[number];

export async function handleJobComplete(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const secret = req.headers['x-webhook-secret'];
    if (secret !== process.env.WEBHOOK_SECRET) {
      res.status(401).json({ status: 'error', message: 'Invalid webhook secret' });
      return;
    }

    const { jobId, status, error, planSummary, executionSummary, securitySummary } = req.body as {
      jobId: string;
      status: string;
      error?: string;
      planSummary?: any;
      executionSummary?: any;
      securitySummary?: any;
    };

    if (!jobId || !status) {
      res.status(400).json({ status: 'error', message: 'jobId and status are required' });
      return;
    }

    if (!ALLOWED_STATUSES.includes(status as JobStatus)) {
      res.status(400).json({ status: 'error', message: `Invalid status: ${status}` });
      return;
    }

    const updateData: Record<string, any> = { status };
    if (planSummary !== undefined) updateData.planSummary = planSummary;
    if (executionSummary !== undefined) updateData.executionSummary = executionSummary;
    if (securitySummary !== undefined) updateData.securitySummary = securitySummary;

    let job = await prisma.analysisJob.update({
      where: { id: jobId },
      data: updateData,
    });

    if (status === 'COMPLETED') {
      const reportSummary = buildReportSummary(job);
      job = await prisma.analysisJob.update({
        where: { id: jobId },
        data: { reportSummary: reportSummary as object },
      });
    }

    const project = await prisma.project.findUnique({ where: { id: job.projectId } });
    if (project) {
      emitJobUpdate(project.ownerId, { event: 'job_updated', job });
    }

    logger.info('Job status updated via webhook', { jobId, status, error });

    res.status(200).json({ job });
  } catch (err) {
    next(err);
  }
}
