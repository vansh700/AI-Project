import { useCallback, useEffect, useState } from 'react';
import * as projectApi from '../api/project.api';
import * as analysisApi from '../api/analysis.api';
import { useJobSocket } from '../hooks/useJobSocket';
import { JobStatusBadge } from '../components/JobStatusBadge';
import { ReportView } from '../components/ReportView';
import type { AnalysisJob, Project, ReportSummary } from '../types/api.types';

interface ProjectPageProps {
  projectId: string;
  onBack: () => void;
}

export function ProjectPage({ projectId, onBack }: ProjectPageProps) {
  const [project, setProject] = useState<Project | null>(null);
  const [jobs, setJobs] = useState<AnalysisJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const refreshJobs = useCallback(() => {
    analysisApi.listJobs(projectId).then(setJobs).catch((err) => setError(err.message));
  }, [projectId]);

  useEffect(() => {
    projectApi.getProject(projectId).then(setProject).catch((err) => setError(err.message));
    refreshJobs();
  }, [projectId, refreshJobs]);

  useJobSocket((updatedJob) => {
    if (updatedJob.projectId !== projectId) return;
    setJobs((prev) => {
      const exists = prev.some((j) => j.id === updatedJob.id);
      if (exists) {
        return prev.map((j) => (j.id === updatedJob.id ? updatedJob : j));
      }
      return [updatedJob, ...prev];
    });
    if (updatedJob.status === 'COMPLETED') {
      analysisApi.getReport(projectId, updatedJob.id).then(setReport).catch(() => {});
      setSelectedJobId(updatedJob.id);
    }
  });

  async function handleUpload(file: File) {
    setBusy(true);
    setError('');
    try {
      const updated = await projectApi.uploadRepository(projectId, file);
      setProject(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setBusy(false);
    }
  }

  async function handleAnalyze() {
    setBusy(true);
    setError('');
    try {
      const job = await analysisApi.triggerAnalysis(projectId);
      setJobs((prev) => [job, ...prev]);
      setSelectedJobId(job.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setBusy(false);
    }
  }

  async function handleViewReport(jobId: string) {
    setSelectedJobId(jobId);
    setReport(null);
    try {
      const data = await analysisApi.getReport(projectId, jobId);
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report');
    }
  }

  return (
    <div>
      <button type="button" className="link-btn" onClick={onBack}>← Back to projects</button>

      {project && (
        <header className="page-header">
          <h2>{project.name}</h2>
          <p className="muted">{project.repoUrl}</p>
        </header>
      )}

      <section className="panel actions-row">
        <label className="file-input">
          Upload ZIP
          <input
            type="file"
            accept=".zip"
            disabled={busy}
            onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
          />
        </label>
        <button type="button" onClick={handleAnalyze} disabled={busy || !project?.storagePath}>
          {busy ? 'Working…' : 'Run Analysis'}
        </button>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="panel">
        <h3>Analysis Jobs</h3>
        {jobs.length === 0 ? (
          <p className="muted">No analysis jobs yet.</p>
        ) : (
          <ul className="job-list">
            {jobs.map((job) => (
              <li key={job.id} className={selectedJobId === job.id ? 'selected' : ''}>
                <div className="job-row">
                  <JobStatusBadge status={job.status} />
                  <span className="muted">{new Date(job.createdAt).toLocaleString()}</span>
                  <code>{job.id.slice(0, 12)}…</code>
                  {job.status === 'COMPLETED' && (
                    <button type="button" onClick={() => handleViewReport(job.id)}>View Report</button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {report && selectedJobId && (
        <section className="panel">
          <ReportView report={report} />
        </section>
      )}
    </div>
  );
}
