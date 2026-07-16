"""Detects the programming language of a file based on its extension."""

# Extension → language name mapping.
# Covers the languages most likely to appear in software repositories.
EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".dockerfile": "Docker",
    ".tf": "Terraform",
    ".graphql": "GraphQL",
    ".proto": "Protobuf",
    ".xml": "XML",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".dart": "Dart",
}


def detect_language(filename: str) -> str:
    """Return the language name for the given filename, or 'Unknown' if not recognised."""
    _, ext = os.path.splitext(filename.lower())
    return EXTENSION_LANGUAGE_MAP.get(ext, "Unknown")


import os  # noqa: E402 — kept at bottom to avoid shadowing built-in at module level
