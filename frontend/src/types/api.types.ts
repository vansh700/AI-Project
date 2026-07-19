export interface Project {
  id: string;
  name: string;
  repoUrl: string;
  storagePath: string | null;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisJob {
  id: string;
  status: string;
  projectId: string;
  planSummary?: Record<string, unknown> | null;
  executionSummary?: Record<string, unknown> | null;
  securitySummary?: Record<string, unknown> | null;
  reportSummary?: ReportSummary | null;
  createdAt: string;
  updatedAt: string;
}

export interface ReportSummary {
  generatedAt: string;
  jobId: string;
  projectId: string;
  status: string;
  overview: {
    language: string;
    framework: string;
    testCases: number;
    testsPassed: number;
    testsFailed: number;
    securityFindings: number;
    criticalFindings: number;
    highFindings: number;
  };
  plan: unknown;
  execution: unknown;
  security: unknown;
}

export interface SecurityFinding {
  id: string;
  ruleId: string;
  severity: string;
  title: string;
  file: string;
  line: number;
  evidence: string;
  recommendation: string;
  type: string;
}
