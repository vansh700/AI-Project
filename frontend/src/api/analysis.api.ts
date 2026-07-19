import { apiFetch } from './client';
import type { AnalysisJob, ReportSummary } from '../types/api.types';

export async function listJobs(projectId: string): Promise<AnalysisJob[]> {
  const data = await apiFetch<{ jobs: AnalysisJob[] }>(`/projects/${projectId}/analysis`);
  return data.jobs;
}

export async function triggerAnalysis(projectId: string): Promise<AnalysisJob> {
  const data = await apiFetch<{ job: AnalysisJob }>(`/projects/${projectId}/analysis`, {
    method: 'POST',
  });
  return data.job;
}

export async function getJob(projectId: string, jobId: string): Promise<AnalysisJob> {
  const data = await apiFetch<{ job: AnalysisJob }>(`/projects/${projectId}/analysis/${jobId}`);
  return data.job;
}

export async function getReport(projectId: string, jobId: string): Promise<ReportSummary> {
  const data = await apiFetch<{ report: ReportSummary }>(
    `/projects/${projectId}/analysis/${jobId}/report`,
  );
  return data.report;
}
