"""CRUD operations for SecurityLog records in the MS2 PostgreSQL database."""
from app.database.db_client import get_session
from app.database.models import SecurityLog
from app.config.logger import get_logger

logger = get_logger("ms2.database.security_repository")


async def save_security_scan(job_id: str, project_id: str, summary: dict) -> None:
    """Create or update a SecurityLog row with status=COMPLETED."""
    async with get_session() as session:
        existing = await _get_by_job_id(session, job_id)
        if existing:
            existing.status = "COMPLETED"
            existing.summary = summary
            existing.error = None
        else:
            session.add(
                SecurityLog(
                    job_id=job_id,
                    project_id=project_id,
                    status="COMPLETED",
                    summary=summary,
                )
            )
    logger.info("save_security_scan | persisted | job_id=%s", job_id)


async def mark_security_failed(job_id: str, error: str) -> None:
    """Create or update a SecurityLog row with status=FAILED."""
    async with get_session() as session:
        existing = await _get_by_job_id(session, job_id)
        if existing:
            existing.status = "FAILED"
            existing.error = error
        else:
            session.add(
                SecurityLog(
                    job_id=job_id,
                    project_id="unknown",
                    status="FAILED",
                    error=error,
                )
            )
    logger.warning("mark_security_failed | job_id=%s error=%s", job_id, error)


async def get_security_by_job_id(job_id: str) -> SecurityLog | None:
    """Retrieve a SecurityLog record by job_id."""
    async with get_session() as session:
        return await _get_by_job_id(session, job_id)


async def _get_by_job_id(session, job_id: str) -> SecurityLog | None:
    from sqlalchemy import select
    result = await session.execute(
        select(SecurityLog).where(SecurityLog.job_id == job_id)
    )
    return result.scalar_one_or_none()
