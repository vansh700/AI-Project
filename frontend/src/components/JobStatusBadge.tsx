export function JobStatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  return <span className={`status status-${normalized}`}>{status}</span>;
}
