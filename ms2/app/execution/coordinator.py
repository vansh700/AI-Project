"""Coordinator — entry point for sandbox test execution after AI planning."""
from app.execution.docker_runner import run_sandbox
from app.database.execution_repository import save_execution, mark_execution_failed
from app.config.logger import get_logger

logger = get_logger("ms2.execution.coordinator")


async def run_execution(
    job_id: str,
    project_id: str,
    repository_path: str,
    language: str,
    framework: str,
    test_cases: list[dict],
) -> dict | None:
    """Execute test cases in a Docker sandbox and persist results.

    Returns the execution summary dict, or None on failure.
    """
    if not test_cases:
        logger.info("run_execution | no test cases | job_id=%s", job_id)
        return None

    logger.info(
        "run_execution | starting | job_id=%s cases=%d lang=%s",
        job_id, len(test_cases), language,
    )

    try:
        summary = run_sandbox(repository_path, language, test_cases)
        summary["framework"] = framework

        await save_execution(job_id=job_id, project_id=project_id, summary=summary)

        logger.info(
            "run_execution | completed | job_id=%s passed=%d failed=%d",
            job_id, summary.get("passed", 0), summary.get("failed", 0),
        )
        return summary

    except Exception as exc:
        logger.error("run_execution | failed | job_id=%s error=%s", job_id, exc)
        await mark_execution_failed(job_id=job_id, error=str(exc))
        return None
