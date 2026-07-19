"""Docker sandbox runner — launches isolated containers for test execution."""
import json
import os
import tempfile
import time
from pathlib import Path

from app.config.logger import get_logger
from app.execution.image_selector import get_sandbox_image
from app.execution.script_builder import build_validation_script

logger = get_logger("ms2.execution.docker_runner")

MEMORY_LIMIT = os.getenv("EXECUTION_MEMORY_LIMIT", "256m")
CPU_QUOTA = int(os.getenv("EXECUTION_CPU_QUOTA", "50000"))
TIMEOUT_SECONDS = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "120"))


def is_docker_available() -> bool:
    """Return True if the Docker daemon is reachable."""
    try:
        import docker
        docker.from_env().ping()
        return True
    except Exception:
        return False


def run_sandbox(
    repository_path: str,
    language: str,
    test_cases: list[dict],
) -> dict:
    """Run test-case validations inside a locked-down Docker container."""
    if not test_cases:
        return _empty_summary(language, "No test cases to execute")

    if os.getenv("DOCKER_ENABLED", "true").lower() == "false":
        logger.warning("Docker execution disabled via DOCKER_ENABLED=false")
        return _mock_summary(language, test_cases, "Docker execution disabled")

    if not is_docker_available():
        logger.warning("Docker daemon unavailable — using mock execution results")
        return _mock_summary(language, test_cases, "Docker daemon unavailable")

    return _run_container(repository_path, language, test_cases)


def _run_container(repository_path: str, language: str, test_cases: list[dict]) -> dict:
    import docker

    image = get_sandbox_image(language)
    script = build_validation_script(test_cases, language)
    start = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="ms2-sandbox-") as sandbox_dir:
        script_path = Path(sandbox_dir) / "run.sh"
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(0o755)

        repo_abs = str(Path(repository_path).resolve())
        client = docker.from_env()

        logger.info(
            "Launching sandbox | image=%s cases=%d repo=%s",
            image, len(test_cases), repo_abs,
        )

        try:
            output = client.containers.run(
                image=image,
                command=["sh", "/sandbox/run.sh"],
                volumes={
                    repo_abs: {"bind": "/repo", "mode": "ro"},
                    sandbox_dir: {"bind": "/sandbox", "mode": "ro"},
                },
                network_mode="none",
                mem_limit=MEMORY_LIMIT,
                cpu_quota=CPU_QUOTA,
                read_only=True,
                tmpfs={"/tmp": "size=64m"},
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
                remove=True,
                stdout=True,
                stderr=True,
                timeout=TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.error("Sandbox container failed | error=%s", exc)
            return _error_summary(language, test_cases, str(exc), start)

    results = _parse_output(output)
    return _build_summary(language, results, start)


def _parse_output(output: bytes | str) -> list[dict]:
    text = output.decode() if isinstance(output, bytes) else output
    text = text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        logger.warning("Failed to parse sandbox output | snippet=%s", text[:200])
    return []


def _build_summary(language: str, results: list[dict], start: float) -> dict:
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    duration_ms = int((time.monotonic() - start) * 1000)

    return {
        "summary": f"Executed {len(results)} tests in {language} sandbox",
        "language": language,
        "totalTests": len(results),
        "passed": passed,
        "failed": failed,
        "skipped": 0,
        "durationMs": duration_ms,
        "sandbox": "docker",
        "results": results,
    }


def _empty_summary(language: str, message: str) -> dict:
    return {
        "summary": message,
        "language": language,
        "totalTests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "durationMs": 0,
        "sandbox": "none",
        "results": [],
    }


def _mock_summary(language: str, test_cases: list[dict], reason: str) -> dict:
    results = [
        {
            "testCaseId": tc.get("id", f"TC-{i + 1:03d}"),
            "target": tc.get("target", ""),
            "status": "skipped",
            "message": reason,
            "durationMs": 0,
        }
        for i, tc in enumerate(test_cases)
    ]
    return {
        "summary": f"Mock execution ({reason})",
        "language": language,
        "totalTests": len(test_cases),
        "passed": 0,
        "failed": 0,
        "skipped": len(test_cases),
        "durationMs": 0,
        "sandbox": "mock",
        "results": results,
    }


def _error_summary(language: str, test_cases: list[dict], error: str, start: float) -> dict:
    duration_ms = int((time.monotonic() - start) * 1000)
    return {
        "summary": f"Sandbox execution failed: {error}",
        "language": language,
        "totalTests": len(test_cases),
        "passed": 0,
        "failed": len(test_cases),
        "skipped": 0,
        "durationMs": duration_ms,
        "sandbox": "docker",
        "results": [],
        "error": error,
    }
