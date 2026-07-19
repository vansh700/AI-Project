"""Coordinator — entry point for dynamic security scanning."""
import time

from app.security.pattern_scanner import scan_files
from app.security.sensitive_file_scanner import scan_sensitive_files
from app.security.auth_probe import probe_auth_coverage
from app.database.security_repository import save_security_scan, mark_security_failed
from app.config.logger import get_logger

logger = get_logger("ms2.security.coordinator")

SEVERITY_ORDER = ("critical", "high", "medium", "low")


async def run_security_scan(
    job_id: str,
    project_id: str,
    files: list,
    language: str,
    framework: str,
) -> dict | None:
    """Run dynamic security scans and persist findings.

    Returns the security summary dict, or None on failure.
    """
    logger.info("run_security_scan | starting | job_id=%s files=%d", job_id, len(files))
    start = time.monotonic()

    try:
        pattern_findings = scan_files(files)
        sensitive_findings = scan_sensitive_files(files)
        auth_findings = probe_auth_coverage(files)

        all_findings = _renumber(pattern_findings + sensitive_findings + auth_findings)
        counts = _count_by_severity(all_findings)
        duration_ms = int((time.monotonic() - start) * 1000)

        summary = {
            "summary": _build_summary_text(counts),
            "language": language,
            "framework": framework,
            "totalFindings": len(all_findings),
            **counts,
            "durationMs": duration_ms,
            "findings": all_findings,
        }

        await save_security_scan(job_id=job_id, project_id=project_id, summary=summary)

        logger.info(
            "run_security_scan | completed | job_id=%s findings=%d critical=%d",
            job_id, len(all_findings), counts.get("critical", 0),
        )
        return summary

    except Exception as exc:
        logger.error("run_security_scan | failed | job_id=%s error=%s", job_id, exc)
        await mark_security_failed(job_id=job_id, error=str(exc))
        return None


def _renumber(findings: list[dict]) -> list[dict]:
    renumbered = []
    for i, finding in enumerate(findings, start=1):
        renumbered.append({**finding, "id": f"SEC-{i:03d}"})
    return renumbered


def _count_by_severity(findings: list[dict]) -> dict:
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "low")
        if sev in counts:
            counts[sev] += 1
    return counts


def _build_summary_text(counts: dict) -> str:
    parts = [f"{counts[s]} {s}" for s in SEVERITY_ORDER if counts.get(s, 0) > 0]
    if not parts:
        return "No security findings detected"
    return f"Found {', '.join(parts)} findings"
