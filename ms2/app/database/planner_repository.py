"""CRUD operations for PlannerState records in the MS2 PostgreSQL database."""
from app.database.db_client import get_session
from app.database.models import PlannerState
from app.config.logger import get_logger

logger = get_logger("ms2.database.planner_repository")


async def save_plan(job_id: str, project_id: str, plan: dict) -> None:
    """Create or update a PlannerState row with status=COMPLETED."""
    async with get_session() as session:
        existing = await _get_by_job_id(session, job_id)
        if existing:
            existing.status = "COMPLETED"
            existing.plan = plan
            existing.error = None
        else:
            session.add(
                PlannerState(
                    job_id=job_id,
                    project_id=project_id,
                    status="COMPLETED",
                    plan=plan,
                )
            )
    logger.info("save_plan | persisted | job_id=%s", job_id)


async def mark_plan_failed(job_id: str, error: str) -> None:
    """Create or update a PlannerState row with status=FAILED."""
    async with get_session() as session:
        existing = await _get_by_job_id(session, job_id)
        if existing:
            existing.status = "FAILED"
            existing.error = error
        else:
            session.add(
                PlannerState(
                    job_id=job_id,
                    project_id="unknown",
                    status="FAILED",
                    error=error,
                )
            )
    logger.warning("mark_plan_failed | job_id=%s error=%s", job_id, error)


async def get_plan_by_job_id(job_id: str) -> PlannerState | None:
    """Retrieve a PlannerState record by job_id."""
    async with get_session() as session:
        return await _get_by_job_id(session, job_id)


async def _get_by_job_id(session, job_id: str) -> PlannerState | None:
    from sqlalchemy import select
    result = await session.execute(
        select(PlannerState).where(PlannerState.job_id == job_id)
    )
    return result.scalar_one_or_none()
