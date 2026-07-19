"""Static pattern-based security scanner for repository source files."""
from app.security.rule_engine import RULES, SecurityRule
from app.config.logger import get_logger

logger = get_logger("ms2.security.pattern_scanner")

SCANNABLE_EXTENSIONS = {
    ".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".go",
    ".rb", ".php", ".cs", ".json", ".yml", ".yaml", ".env",
}
MAX_FILE_BYTES = 512_000
MAX_FINDINGS = 100


def scan_files(files: list) -> list[dict]:
    """Scan repository files against security rules and return findings."""
    findings: list[dict] = []
    counter = 0

    for file_node in files:
        ext = file_node.extension.lower()
        if ext not in SCANNABLE_EXTENSIONS:
            continue

        try:
            with open(file_node.path, encoding="utf-8", errors="ignore") as fh:
                content = fh.read(MAX_FILE_BYTES)
        except OSError:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            for rule in RULES:
                if rule.extensions and ext not in rule.extensions:
                    continue
                if rule.pattern.search(line):
                    counter += 1
                    findings.append(_make_finding(counter, rule, file_node.relative_path, line_no, line))
                    if len(findings) >= MAX_FINDINGS:
                        logger.warning("pattern_scanner | hit MAX_FINDINGS=%d", MAX_FINDINGS)
                        return findings

    logger.info("pattern_scanner | completed | findings=%d", len(findings))
    return findings


def _make_finding(counter: int, rule: SecurityRule, file_path: str, line_no: int, line: str) -> dict:
    evidence = line.strip()[:120]
    return {
        "id": f"SEC-{counter:03d}",
        "ruleId": rule.id,
        "severity": rule.severity,
        "title": rule.title,
        "file": file_path.replace("\\", "/"),
        "line": line_no,
        "evidence": evidence,
        "recommendation": rule.recommendation,
        "type": "pattern",
    }
