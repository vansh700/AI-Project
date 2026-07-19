"""Dynamic auth-coverage probe — flags route files lacking auth references."""
from app.config.logger import get_logger

logger = get_logger("ms2.security.auth_probe")

ROUTE_INDICATORS = ("route", "router", "endpoint", "controller")
AUTH_INDICATORS = ("auth", "jwt", "authenticate", "authorize", "middleware", "guard", "passport")


def probe_auth_coverage(files: list) -> list[dict]:
    """Flag route/controller files that show no authentication references."""
    findings: list[dict] = []
    counter = 0

    for file_node in files:
        rel = file_node.relative_path.replace("\\", "/").lower()
        if not any(ind in rel for ind in ROUTE_INDICATORS):
            continue
        if file_node.extension.lower() not in {".js", ".ts", ".py"}:
            continue

        try:
            with open(file_node.path, encoding="utf-8", errors="ignore") as fh:
                content = fh.read(100_000).lower()
        except OSError:
            continue

        if any(ind in content for ind in AUTH_INDICATORS):
            continue

        counter += 1
        findings.append({
            "id": f"SEC-{counter:03d}",
            "ruleId": "missing-auth-coverage",
            "severity": "medium",
            "title": "Route/controller file with no auth references",
            "file": file_node.relative_path.replace("\\", "/"),
            "line": 0,
            "evidence": f"No auth middleware detected in {rel}",
            "recommendation": "Ensure protected endpoints use authentication middleware.",
            "type": "dynamic-probe",
        })

    logger.info("auth_probe | completed | findings=%d", len(findings))
    return findings
