import type { ReportSummary, SecurityFinding } from '../types/api.types';
import { JobStatusBadge } from './JobStatusBadge';

interface ReportViewProps {
  report: ReportSummary;
}

export function ReportView({ report }: ReportViewProps) {
  const { overview } = report;
  const findings = ((report.security as { findings?: SecurityFinding[] })?.findings) ?? [];

  return (
    <div className="report">
      <div className="report-header">
        <h2>Analysis Report</h2>
        <JobStatusBadge status={report.status} />
        <p className="muted">Generated {new Date(report.generatedAt).toLocaleString()}</p>
      </div>

      <div className="stats-grid">
        <StatCard label="Language" value={overview.language} />
        <StatCard label="Framework" value={overview.framework} />
        <StatCard label="Test Cases" value={String(overview.testCases)} />
        <StatCard label="Tests Passed" value={String(overview.testsPassed)} />
        <StatCard label="Tests Failed" value={String(overview.testsFailed)} />
        <StatCard label="Security Findings" value={String(overview.securityFindings)} />
        <StatCard label="Critical" value={String(overview.criticalFindings)} highlight />
        <StatCard label="High" value={String(overview.highFindings)} />
      </div>

      {findings.length > 0 && (
        <section className="panel">
          <h3>Security Findings</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Severity</th>
                  <th>Title</th>
                  <th>File</th>
                </tr>
              </thead>
              <tbody>
                {findings.map((f) => (
                  <tr key={f.id}>
                    <td>{f.id}</td>
                    <td className={`severity-${f.severity}`}>{f.severity}</td>
                    <td>{f.title}</td>
                    <td><code>{f.file}{f.line ? `:${f.line}` : ''}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {report.plan != null && (
        <section className="panel">
          <h3>Test Plan Summary</h3>
          <pre>{JSON.stringify(report.plan, null, 2)}</pre>
        </section>
      )}
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`stat-card${highlight ? ' stat-highlight' : ''}`}>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
    </div>
  );
}
