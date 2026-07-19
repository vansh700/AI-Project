"""Coordinator — single entry point for running the AI planner.

Callers (e.g., the BullMQ worker) invoke run_planner() with job metadata.
This function orchestrates the LangGraph execution and persists results
to the MS2 PostgreSQL database via planner_repository.
"""
from app.planner.graph import get_planner_graph
from app.database.planner_repository import save_plan, mark_plan_failed
from app.config.logger import get_logger

logger = get_logger("ms2.planner.coordinator")


async def run_planner(
    job_id: str,
    project_id: str,
    repository_path: str,
    language: str,
    framework: str,
) -> dict | None:
    """Run the LangGraph planning pipeline and return the generated plan dict.

    Returns None if planning fails (errors are logged and persisted).
    """
    logger.info(
        "run_planner | starting | job_id=%s project_id=%s", job_id, project_id
    )

    initial_state = {
        "analysisId": job_id,
        "repositoryPath": repository_path,
        "language": language,
        "framework": framework,
        "graph": {},
        "plan": None,
        "testCases": [],
        "executionResults": [],
        "findings": [],
        "report": None,
    }

    graph = get_planner_graph()

    try:
        final_state = await graph.ainvoke(initial_state)
        plan = final_state.get("plan")
        test_cases = final_state.get("testCases", [])

        await save_plan(job_id=job_id, project_id=project_id, plan={
            "plan": plan,
            "testCases": test_cases,
        })

        logger.info(
            "run_planner | completed | job_id=%s testCases=%d",
            job_id,
            len(test_cases),
        )
        return plan

    except Exception as exc:
        logger.error("run_planner | failed | job_id=%s error=%s", job_id, exc)
        await mark_plan_failed(job_id=job_id, error=str(exc))
        return None
