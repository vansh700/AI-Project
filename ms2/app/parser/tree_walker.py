"""Walks an extracted repository directory and builds a structured file tree."""
import os
from dataclasses import dataclass
from app.parser.language_detector import detect_language
from app.config.logger import get_logger

logger = get_logger("ms2.parser.tree_walker")

# Directories that are always ignored — they are never part of source code
IGNORED_DIRS = {
    ".git", ".svn", "node_modules", "__pycache__", ".pytest_cache",
    "venv", ".venv", "dist", "build", ".next", ".nuxt", "coverage",
}


@dataclass
class FileNode:
    """Represents a single file in the repository."""
    path: str          # absolute path on disk
    relative_path: str # path relative to the repo root
    name: str          # filename
    extension: str     # file extension (including dot)
    language: str      # detected language
    size_bytes: int    # file size in bytes


@dataclass
class DirectoryNode:
    """Represents a directory in the repository."""
    path: str           # absolute path on disk
    relative_path: str  # path relative to the repo root
    name: str           # directory name


@dataclass
class RepositoryTree:
    """The complete, walked representation of the repository."""
    root_path: str
    directories: list[DirectoryNode]
    files: list[FileNode]


def walk_repository(root_path: str) -> RepositoryTree:
    """
    Walk the directory tree at root_path and build a RepositoryTree.
    Skips ignored directories and zero-byte or too-large files (>10 MB).
    """
    directories: list[DirectoryNode] = []
    files: list[FileNode] = []

    logger.info("Walking repository tree | root=%s", root_path)

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        # Prune ignored directories in-place (os.walk skips them)
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        relative_dir = os.path.relpath(dirpath, root_path)

        if relative_dir != ".":  # skip the root itself — it is the Repository node
            directories.append(DirectoryNode(
                path=dirpath,
                relative_path=relative_dir,
                name=os.path.basename(dirpath),
            ))

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            size = os.path.getsize(file_path)

            if size > 10 * 1024 * 1024:  # skip files larger than 10 MB
                logger.debug("Skipping large file | path=%s size=%d", file_path, size)
                continue

            _, ext = os.path.splitext(filename)
            files.append(FileNode(
                path=file_path,
                relative_path=os.path.relpath(file_path, root_path),
                name=filename,
                extension=ext.lower(),
                language=detect_language(filename),
                size_bytes=size,
            ))

    logger.info(
        "Walk complete | dirs=%d files=%d",
        len(directories), len(files),
    )
    return RepositoryTree(root_path=root_path, directories=directories, files=files)
