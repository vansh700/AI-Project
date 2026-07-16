"""Neo4j driver singleton for MS2.

All graph operations import this driver — never instantiate one directly elsewhere.
"""
import os
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config.logger import get_logger

logger = get_logger("ms2.config.neo4j")

_driver: AsyncDriver | None = None


def get_driver() -> AsyncDriver:
    """Return the singleton Neo4j async driver. Initialised on first call."""
    global _driver
    if _driver is None:
        url = os.getenv("NEO4J_URL", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "neo4j_password")
        _driver = AsyncGraphDatabase.driver(url, auth=(user, password))
        logger.info("Neo4j driver initialised | url=%s user=%s", url, user)
    return _driver


async def close_driver() -> None:
    """Gracefully close the Neo4j driver on shutdown."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None
        logger.info("Neo4j driver closed.")
