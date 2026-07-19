"""Map detected repository language to a sandbox Docker image."""

LANGUAGE_IMAGES: dict[str, str] = {
    "JavaScript": "node:20-alpine",
    "TypeScript": "node:20-alpine",
    "JavaScript (React)": "node:20-alpine",
    "TypeScript (React)": "node:20-alpine",
    "Python": "python:3.12-alpine",
    "Go": "golang:1.22-alpine",
    "Java": "eclipse-temurin:21-jdk-alpine",
}

DEFAULT_IMAGE = "node:20-alpine"


def get_sandbox_image(language: str) -> str:
    """Return the Docker image tag for the given repository language."""
    return LANGUAGE_IMAGES.get(language, DEFAULT_IMAGE)
