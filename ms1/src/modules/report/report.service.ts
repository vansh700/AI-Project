import { AnalysisJob } from '@prisma/client';

export interface ReportOverview {
  language: string;
  framework: string;
  testCases: number;
  testsPassed: number;
  testsFailed: number;
  securityFindings: number;
  criticalFindings: number;
  highFindings: number;
}

export interface ReportSummary {
  generatedAt: string;
  jobId: string;
  projectId: string;
  status: string;
  overview: ReportOverview;
  plan: unknown;
  execution: unknown;
  security: unknown;
}

export function buildReportSummary(job: AnalysisJob): ReportSummary {
  const plan = job.planSummary as Record<string, unknown> | null;
  const execution = job.executionSummary as Record<string, unknown> | null;
  const security = job.securitySummary as Record<string, unknown> | null;

  return {
    generatedAt: new Date().toISOString(),
    jobId: job.id,
    projectId: job.projectId,
    status: job.status,
    overview: {
      language: String(plan?.language ?? execution?.language ?? 'Unknown'),
      framework: String(plan?.framework ?? execution?.framework ?? 'unknown'),
      testCases: Number(plan?.testCases ? (plan.testCases as unknown[]).length : 0),
      testsPassed: Number(execution?.passed ?? 0),
      testsFailed: Number(execution?.failed ?? 0),
      securityFindings: Number(security?.totalFindings ?? 0),
      criticalFindings: Number(security?.critical ?? 0),
      highFindings: Number(security?.high ?? 0),
    },
    plan: plan ?? null,
    execution: execution ?? null,
    security: security ?? null,
  };
}
