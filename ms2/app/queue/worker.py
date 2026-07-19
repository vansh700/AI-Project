"""
MS2 BullMQ Worker.

Consumes jobs from 'analysis-queue' and runs the full analysis pipeline:
  1. Extract the uploaded .zip archive
  2. Walk the repository file tree
  3. Build the Neo4j knowledge graph
  4. Run AI planner (LangGraph)
  5. Execute test plan in Docker sandbox
  6. Run dynamic security scan
  7. Notify MS1 via webhook (COMPLETED or FAILED)
"""
import os
import shutil
from bullmq import Worker
from app.config.logger import get_logger
from app.parser.zip_extractor import extract_zip
from app.parser.tree_walker import walk_repository
from app.graph.graph_builder import build_graph
from app.services.webhook import notify_job_complete, notify_job_failed, notify_job_running
from app.planner.coordinator import run_planner
from app.execution.coordinator import run_execution
from app.security.coordinator import run_security_scan

logger = get_logger("ms2.queue.worker")

QUEUE_NAME = "analysis-queue"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def _parse_redis_connection(url: str) -> dict:
    """Parse redis URL into a connection dict for bullmq."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
    }


def _detect_language_and_framework(tree) -> tuple[str, str]:
    """Inspect repository file tree to guess primary language and framework."""
    from collections import Counter
    # Count file extensions mapped to languages
    langs = [f.language for f in tree.files if f.language and f.language != "Unknown"]
    primary_lang = Counter(langs).most_common(1)[0][0] if langs else "Unknown"

    framework = "unknown"
    file_names = {f.name.lower() for f in tree.files}

    if primary_lang in ["JavaScript", "TypeScript", "TypeScript (React)", "JavaScript (React)"]:
        if "next.config.js" in file_names or "next.config.mjs" in file_names:
            framework = "Next.js"
        elif "vite.config.ts" in file_names or "vite.config.js" in file_names:
            framework = "Vite/React"
        else:
            framework = "Express"
    elif primary_lang == "Python":
        framework = "FastAPI"
    elif primary_lang == "Go":
        framework = "Go Gin"
    elif primary_lang == "Java":
        framework = "Spring Boot"

    return primary_lang, framework


async def process_job(job, job_token):
    """
    Full Phase 8 pipeline:
    extract → walk → build graph → AI planner → Docker execution → security scan → webhook
    """
    bull_job_id = job.id
    data = job.data

    db_job_id = data.get("jobId", "")
    project_id = data.get("projectId", "")
    storage_path = data.get("storagePath", "")

    logger.info(
        "Job received | bullJobId=%s dbJobId=%s projectId=%s",
        bull_job_id, db_job_id, project_id,
    )

    await notify_job_running(bull_job_id, db_job_id)

    extract_dir: str | None = None
    try:
        # Step 1: Extract
        extract_dir = extract_zip(storage_path)

        # Step 2: Walk
        tree = walk_repository(extract_dir)

        # Step 3: Build Neo4j graph
        await build_graph(db_job_id, project_id, tree)

        # Step 4: Run AI Planner (LangGraph)
        primary_lang, framework = _detect_language_and_framework(tree)
        logger.info(
            "Detected environment | lang=%s framework=%s. Running AI planner...",
            primary_lang, framework
        )
        
        plan = None
        try:
            plan = await run_planner(
                job_id=db_job_id,
                project_id=project_id,
                repository_path=extract_dir,
                language=primary_lang,
                framework=framework
            )
        except Exception as planner_err:
            logger.error(
                "AI Planner failed | dbJobId=%s error=%s. Proceeding without plan.",
                db_job_id, str(planner_err), exc_info=True
            )

        # Step 5: Execute test plan in Docker sandbox
        execution_summary = None
        test_cases = (plan or {}).get("testCases", [])
        if test_cases:
            try:
                execution_summary = await run_execution(
                    job_id=db_job_id,
                    project_id=project_id,
                    repository_path=extract_dir,
                    language=primary_lang,
                    framework=framework,
                    test_cases=test_cases,
                )
            except Exception as exec_err:
                logger.error(
                    "Docker execution failed | dbJobId=%s error=%s. Proceeding without results.",
                    db_job_id, str(exec_err), exc_info=True
                )

        # Step 6: Dynamic security scan
        security_summary = None
        try:
            security_summary = await run_security_scan(
                job_id=db_job_id,
                project_id=project_id,
                files=tree.files,
                language=primary_lang,
                framework=framework,
            )
        except Exception as sec_err:
            logger.error(
                "Security scan failed | dbJobId=%s error=%s. Proceeding without findings.",
                db_job_id, str(sec_err), exc_info=True
            )

        # Step 7: Notify MS1 of completion
        await notify_job_complete(
            bull_job_id, db_job_id,
            plan_summary=plan,
            execution_summary=execution_summary,
            security_summary=security_summary,
        )

        logger.info(
            "Job completed | dbJobId=%s dirs=%d files=%d with_plan=%s with_execution=%s with_security=%s",
            db_job_id, len(tree.directories), len(tree.files),
            str(plan is not None), str(execution_summary is not None),
            str(security_summary is not None),
        )
        return {"status": "COMPLETED", "jobId": db_job_id}

    except Exception as exc:
        logger.error("Job failed | dbJobId=%s error=%s", db_job_id, str(exc), exc_info=True)
        await notify_job_failed(bull_job_id, db_job_id, str(exc))
        raise  # re-raise so BullMQ marks the job as failed and schedules retry

    finally:
        # Always clean up the temp directory
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.debug("Temp directory cleaned up | path=%s", extract_dir)


def create_worker() -> Worker:
    """Create and return a BullMQ Worker instance connected to Redis."""
    connection = _parse_redis_connection(REDIS_URL)
    logger.info(
        "Starting BullMQ worker on queue '%s' | redis=%s:%d",
        QUEUE_NAME, connection["host"], connection["port"],
    )
    return Worker(QUEUE_NAME, process_job, {"connection": connection})
