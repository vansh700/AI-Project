import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.health.health_router import router as health_router
from app.queue.worker import create_worker
from app.config.neo4j_client import close_driver
from app.config.logger import get_logger
from app.database.db_client import create_tables, close_engine


logger = get_logger(__name__)

_worker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start BullMQ worker and initialize database on startup; close gracefully on shutdown."""
    global _worker
    logger.info(
        "MS2 Worker started on port %s | env=%s",
        os.getenv("PORT", "8000"),
        os.getenv("ENVIRONMENT", "development"),
    )
    # Initialize MS2 PostgreSQL database tables
    try:
        await create_tables()
    except Exception as e:
        logger.error("Failed to initialize MS2 PostgreSQL database: %s", e, exc_info=True)

    _worker = create_worker()
    yield
    if _worker:
        await _worker.close()
    await close_driver()
    await close_engine()
    logger.info("MS2 Worker shutdown complete.")


app = FastAPI(
    title="MS2 Worker API",
    version="1.0.0",
    lifespan=lifespan,
    # Disable public docs — MS2 is never exposed to the internet
    docs_url=None,
    redoc_url=None,
)

app.include_router(health_router)
