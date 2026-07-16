import { AnalysisJob } from '@prisma/client';
import { prisma } from '../../config/prisma.client';

export async function createAnalysisJob(projectId: string): Promise<AnalysisJob> {
  return prisma.analysisJob.create({
    data: { projectId, status: 'QUEUED' },
  });
}

export async function findJobsByProject(projectId: string): Promise<AnalysisJob[]> {
  return prisma.analysisJob.findMany({
    where: { projectId },
    orderBy: { createdAt: 'desc' },
  });
}
