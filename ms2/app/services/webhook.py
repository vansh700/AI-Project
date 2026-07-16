"""
Sends job completion webhook callbacks to MS1.

MS2 must never call MS1 HTTP APIs directly for processing requests.
This is the ONLY exception: a completion callback is sent after a job
finishes so MS1 can update the AnalysisJob status in its database.
"""
import os
import aiohttp
from dotenv import load_dotenv
load_dotenv()
from app.config.logger import get_logger

logger = get_logger("ms2.services.webhook")

MS1_WEBHOOK_URL = os.getenv("MS1_WEBHOOK_URL", "http://localhost:3000/webhooks")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


async def notify_job_complete(job_id: str, db_job_id: str) -> None:
    """POST to MS1 webhook signalling the analysis job completed successfully."""
    await _send(db_job_id, "COMPLETED", None)


async def notify_job_failed(job_id: str, db_job_id: str, error: str) -> None:
    """POST to MS1 webhook signalling the analysis job failed."""
    await _send(db_job_id, "FAILED", error)


async def _send(db_job_id: str, status: str, error: str | None) -> None:
    url = f"{MS1_WEBHOOK_URL}/job-complete"
    payload = {"jobId": db_job_id, "status": status}
    if error:
        payload["error"] = error

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Secret": WEBHOOK_SECRET,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    logger.info("Webhook delivered | jobId=%s status=%s", db_job_id, status)
                else:
                    body = await resp.text()
                    logger.warning("Webhook returned non-200 | status=%d body=%s", resp.status, body)
    except Exception as exc:
        # Webhook failure must NEVER crash the worker — log and move on
        logger.error("Webhook delivery failed | jobId=%s error=%s", db_job_id, str(exc))
