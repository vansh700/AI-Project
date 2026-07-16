import logging
import sys
from os import getenv


LOG_LEVEL = logging.DEBUG if getenv("ENVIRONMENT") != "production" else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. All loggers share the root configuration above."""
    return logging.getLogger(name)
