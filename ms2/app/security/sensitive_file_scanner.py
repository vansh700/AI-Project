"""Detect sensitive or credential files committed to the repository."""
from app.security.rule_engine import SENSITIVE_FILES
from app.config.logger import get_logger

logger = get_logger("ms2.security.sensitive_file_scanner")


def scan_sensitive_files(files: list) -> list[dict]:
    """Flag files whose names match known sensitive file patterns."""
    findings: list[dict] = []
    counter = 0

    for file_node in files:
        name_lower = file_node.name.lower()
        rel_path = file_node.relative_path.replace("\\", "/")

        for pattern, meta in SENSITIVE_FILES.items():
            if name_lower == pattern or name_lower.endswith(pattern):
                counter += 1
                findings.append({
                    "id": f"SEC-{counter:03d}",
                    "ruleId": f"sensitive-file-{pattern}",
                    "severity": meta["severity"],
                    "title": meta["title"],
                    "file": rel_path,
                    "line": 0,
                    "evidence": f"Sensitive file found: {rel_path}",
                    "recommendation": "Remove from repository and add to .gitignore; rotate any exposed credentials.",
                    "type": "sensitive-file",
                })
                break

    logger.info("sensitive_file_scanner | completed | findings=%d", len(findings))
    return findings
