"""
MS2 BullMQ Worker.

Consumes jobs from 'analysis-queue' and runs the Phase 5 repository
intelligence pipeline:
  1. Extract the uploaded .zip archive
  2. Walk the repository file tree
  3. Build the Neo4j knowledge graph
  4. Notify MS1 via webhook (COMPLETED or FAILED)
"""
import os
import shutil
from bullmq import Worker
from app.config.logger import get_logger
from app.parser.zip_extractor import extract_zip
from app.parser.tree_walker import walk_repository
from app.graph.graph_builder import build_graph
from app.services.webhook import notify_job_complete, notify_job_failed

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


async def process_job(job, job_token):
    """
    Full Phase 5 pipeline:
    extract → walk → build graph → webhook
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

    extract_dir: str | None = None
    try:
        # Step 1: Extract
        extract_dir = extract_zip(storage_path)

        # Step 2: Walk
        tree = walk_repository(extract_dir)

        # Step 3: Build Neo4j graph
        await build_graph(db_job_id, project_id, tree)

        # Step 4: Notify MS1 of completion
        await notify_job_complete(bull_job_id, db_job_id)

        logger.info(
            "Job completed | dbJobId=%s dirs=%d files=%d",
            db_job_id, len(tree.directories), len(tree.files),
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
