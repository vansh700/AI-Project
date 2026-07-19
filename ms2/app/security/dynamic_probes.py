"""Dynamic security probes — heuristic checks beyond static pattern matching."""
from app.parser.tree_walker import RepositoryTree
from app.security.rule_engine import SENSITIVE_FILENAMES
from app.config.logger import get_logger

logger = get_logger("ms2.security.dynamic_probes")

UNPROTECTED_ROUTE_HINTS = ("router.get(", "router.post(", "app.get(", "app.post(")
AUTH_HINTS = ("authenticate", "jwt", "authMiddleware", "requireAuth", "verifyToken")


def run_dynamic_probes(tree: RepositoryTree, language: str, framework: str) -> list[dict]:
    """Run dynamic heuristic probes against the repository tree."""
    findings: list[dict] = []
    counter = 0

    counter, findings = _probe_sensitive_files(tree, counter, findings)
    counter, findings = _probe_missing_lockfile(tree, counter, findings)
    counter, findings = _probe_unprotected_routes(tree, counter, findings, language)

    logger.info("Dynamic probes complete | findings=%d", len(findings))
    return findings


def _probe_sensitive_files(tree: RepositoryTree, counter: int, findings: list[dict]) -> tuple[int, list[dict]]:
    for file_node in tree.files:
        name = file_node.name.lower()
        rel = file_node.relative_path.replace("\\", "/")
        if name not in SENSITIVE_FILENAMES and not rel.endswith("/.env"):
            continue
        counter += 1
        findings.append({
            "id": f"SEC-{counter:03d}",
            "ruleId": "sensitive-file-exposed",
            "severity": "critical",
            "title": "Sensitive file committed to repository",
            "file": rel,
            "line": 0,
            "evidence": f"File present: {rel}",
            "recommendation": "Remove sensitive files and add them to .gitignore.",
            "scanType": "dynamic",
        })
    return counter, findings


def _probe_missing_lockfile(tree: RepositoryTree, counter: int, findings: list[dict]) -> tuple[int, list[dict]]:
    names = {f.name.lower() for f in tree.files}
    has_package_json = "package.json" in names
    has_lock = "package-lock.json" in names or "yarn.lock" in names or "pnpm-lock.yaml" in names

    if has_package_json and not has_lock:
        counter += 1
        findings.append({
            "id": f"SEC-{counter:03d}",
            "ruleId": "missing-lockfile",
            "severity": "medium",
            "title": "Missing dependency lock file",
            "file": "package.json",
            "line": 0,
            "evidence": "package.json found without lock file",
            "recommendation": "Commit a lock file to ensure reproducible and auditable builds.",
            "scanType": "dynamic",
        })
    return counter, findings


def _probe_unprotected_routes(
    tree: RepositoryTree, counter: int, findings: list[dict], language: str
) -> tuple[int, list[dict]]:
    if language not in {"JavaScript", "TypeScript", "JavaScript (React)", "TypeScript (React)"}:
        return counter, findings

    for file_node in tree.files:
        if "route" not in file_node.relative_path.lower() and "router" not in file_node.name.lower():
            continue
        if file_node.extension not in {".js", ".ts"}:
            continue

        try:
            content = open(file_node.path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue

        if not any(hint in content for hint in UNPROTECTED_ROUTE_HINTS):
            continue
        if any(hint in content for hint in AUTH_HINTS):
            continue

        counter += 1
        rel = file_node.relative_path.replace("\\", "/")
        findings.append({
            "id": f"SEC-{counter:03d}",
            "ruleId": "unprotected-routes",
            "severity": "high",
            "title": "Route file may lack authentication middleware",
            "file": rel,
            "line": 0,
            "evidence": "Route handlers found without auth middleware references",
            "recommendation": "Apply authentication middleware to protected routes.",
            "scanType": "dynamic",
        })

    return counter, findings
