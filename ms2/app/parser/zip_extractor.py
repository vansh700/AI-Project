"""Extracts a repository zip archive to a temporary directory."""
import os
import zipfile
import tempfile
from app.config.logger import get_logger

logger = get_logger("ms2.parser.zip_extractor")


def extract_zip(storage_path: str) -> str:
    """
    Extract the zip at storage_path to a uniquely named temp directory.
    Returns the path to the extracted root directory.
    Raises FileNotFoundError if the zip does not exist.
    """
    if not os.path.exists(storage_path):
        raise FileNotFoundError(f"Repository archive not found: {storage_path}")

    if not zipfile.is_zipfile(storage_path):
        raise ValueError(f"File is not a valid zip archive: {storage_path}")

    extract_dir = tempfile.mkdtemp(prefix="ms2_repo_")
    logger.info("Extracting zip | src=%s dest=%s", storage_path, extract_dir)

    with zipfile.ZipFile(storage_path, "r") as zf:
        zf.extractall(extract_dir)

    logger.info("Extraction complete | dest=%s", extract_dir)
    return extract_dir
