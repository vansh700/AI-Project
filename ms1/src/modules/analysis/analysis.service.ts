import { AnalysisJob } from '@prisma/client';
import { getProjectDetail } from '../project/project.service';
import { createAnalysisJob, findJobsByProject } from './analysis.repository';
import { analysisQueue } from '../../config/queue';

export interface AnalysisJobPayload {
  jobId: string;
  projectId: string;
  storagePath: string;
  userId: string;
}

export async function triggerAnalysis(projectId: string, userId: string): Promise<AnalysisJob> {
  const project = await getProjectDetail(projectId, userId);

  if (!project.storagePath) {
    throw Object.assign(
      new Error('Repository must be uploaded before analysis can be triggered'),
      { statusCode: 422 }
    );
  }

  // Create the DB record first so we have a jobId to pass into the queue
  const job = await createAnalysisJob(projectId);

  const payload: AnalysisJobPayload = {
    jobId: job.id,
    projectId,
    storagePath: project.storagePath,
    userId,
  };

  // Enqueue — MS2 picks this up asynchronously; MS1 never waits for it
  await analysisQueue.add('analyse-repository', payload, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 5000 },
  });

  return job;
}

export async function getAnalysisJobs(projectId: string, userId: string): Promise<AnalysisJob[]> {
  // Verify ownership before exposing job data
  await getProjectDetail(projectId, userId);
  return findJobsByProject(projectId);
}
