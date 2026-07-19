"""Security rule definitions for dynamic repository scanning."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SecurityRule:
    id: str
    title: str
    severity: str
    pattern: re.Pattern
    recommendation: str
    extensions: frozenset[str] | None = None


RULES: list[SecurityRule] = [
    SecurityRule(
        id="hardcoded-secret",
        title="Hardcoded secret or API key",
        severity="critical",
        pattern=re.compile(
            r"(?i)(api[_-]?key|secret|password|token|auth)\s*[=:]\s*['\"][^'\"]{8,}['\"]"
        ),
        recommendation="Move secrets to environment variables or a secrets manager.",
    ),
    SecurityRule(
        id="sql-injection-risk",
        title="Potential SQL injection via string concatenation",
        severity="high",
        pattern=re.compile(r"(?i)(query|execute)\s*\(\s*['\"].*\+.*['\"]"),
        recommendation="Use parameterized queries or an ORM instead of string concatenation.",
        extensions=frozenset({".js", ".ts", ".py", ".java", ".go"}),
    ),
    SecurityRule(
        id="dangerous-eval",
        title="Use of eval() or exec()",
        severity="high",
        pattern=re.compile(r"\b(eval|exec)\s*\("),
        recommendation="Avoid dynamic code execution; use safe parsing alternatives.",
        extensions=frozenset({".js", ".ts", ".py"}),
    ),
    SecurityRule(
        id="insecure-crypto",
        title="Weak cryptographic hash for passwords",
        severity="medium",
        pattern=re.compile(r"(?i)(md5|sha1)\s*\(.*password"),
        recommendation="Use bcrypt, scrypt, or argon2 for password hashing.",
    ),
    SecurityRule(
        id="cors-wildcard",
        title="CORS configured with wildcard origin",
        severity="medium",
        pattern=re.compile(r"(?i)Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]?\*"),
        recommendation="Restrict CORS to specific trusted origins.",
        extensions=frozenset({".js", ".ts", ".py"}),
    ),
    SecurityRule(
        id="debug-enabled",
        title="Debug mode enabled in configuration",
        severity="low",
        pattern=re.compile(r"(?i)(debug|NODE_ENV)\s*[=:]\s*['\"]?(true|development|1)['\"]?"),
        recommendation="Disable debug mode in production environments.",
    ),
    SecurityRule(
        id="jwt-none-algorithm",
        title="JWT algorithm set to 'none'",
        severity="critical",
        pattern=re.compile(r"(?i)algorithm\s*[=:]\s*['\"]none['\"]"),
        recommendation="Never allow the 'none' JWT algorithm; enforce RS256 or HS256.",
    ),
    SecurityRule(
        id="insecure-random",
        title="Use of Math.random() for security-sensitive operations",
        severity="medium",
        pattern=re.compile(r"Math\.random\s*\(\)"),
        recommendation="Use crypto.randomBytes() or crypto.getRandomValues() for tokens.",
        extensions=frozenset({".js", ".ts"}),
    ),
]

SENSITIVE_FILES: dict[str, dict] = {
    ".env": {"severity": "critical", "title": "Environment file committed to repository"},
    ".env.local": {"severity": "critical", "title": "Local environment file committed"},
    "id_rsa": {"severity": "critical", "title": "Private SSH key committed"},
    "credentials.json": {"severity": "critical", "title": "Credentials file committed"},
    ".pem": {"severity": "high", "title": "Certificate/key file committed"},
    ".key": {"severity": "high", "title": "Private key file committed"},
    "secrets.yml": {"severity": "high", "title": "Secrets configuration committed"},
    "aws_credentials": {"severity": "critical", "title": "AWS credentials file committed"},
}
