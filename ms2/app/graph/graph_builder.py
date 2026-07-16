"""
Builds the repository knowledge graph in Neo4j.

Graph schema:
  (:Repository {jobId, projectId, rootPath, createdAt})
  (:Directory  {path, name})
  (:File       {path, name, extension, language, sizeBytes})

Relationships:
  (Repository)-[:HAS_DIRECTORY]->(Directory)
  (Directory)-[:CONTAINS]->(File)
  (Directory)-[:CONTAINS]->(Directory)   [subdirectory nesting]
"""
import os
from datetime import datetime, timezone
from app.config.neo4j_client import get_driver
from app.parser.tree_walker import RepositoryTree
from app.config.logger import get_logger

logger = get_logger("ms2.graph.graph_builder")


async def build_graph(job_id: str, project_id: str, tree: RepositoryTree) -> None:
    """
    Persist the full repository knowledge graph into Neo4j.
    Clears any previous graph for the same jobId before writing.
    """
    driver = get_driver()

    async with driver.session() as session:
        logger.info("Building graph | jobId=%s projectId=%s", job_id, project_id)

        # Clear stale data for this job in case of a retry
        await session.run(
            "MATCH (r:Repository {jobId: $jobId}) DETACH DELETE r",
            jobId=job_id,
        )

        # Create the root Repository node
        await session.run(
            """
            CREATE (:Repository {
                jobId:     $jobId,
                projectId: $projectId,
                rootPath:  $rootPath,
                createdAt: $createdAt
            })
            """,
            jobId=job_id,
            projectId=project_id,
            rootPath=tree.root_path,
            createdAt=datetime.now(timezone.utc).isoformat(),
        )

        # Create all Directory nodes and link them to the Repository
        for directory in tree.directories:
            parent_path = os.path.dirname(directory.path)
            parent_relative = os.path.relpath(parent_path, tree.root_path)

            await session.run(
                """
                MERGE (d:Directory {path: $path})
                SET d.name = $name, d.relativePath = $relativePath
                """,
                path=directory.path,
                name=directory.name,
                relativePath=directory.relative_path,
            )

            if parent_relative == ".":
                # Direct child of root — link to Repository
                await session.run(
                    """
                    MATCH (r:Repository {jobId: $jobId})
                    MATCH (d:Directory {path: $path})
                    MERGE (r)-[:HAS_DIRECTORY]->(d)
                    """,
                    jobId=job_id,
                    path=directory.path,
                )
            else:
                # Subdirectory — link to parent Directory
                await session.run(
                    """
                    MATCH (parent:Directory {path: $parentPath})
                    MATCH (child:Directory {path: $childPath})
                    MERGE (parent)-[:CONTAINS]->(child)
                    """,
                    parentPath=parent_path,
                    childPath=directory.path,
                )

        # Create all File nodes and link them to their parent Directory (or Repository)
        for file_node in tree.files:
            parent_path = os.path.dirname(file_node.path)
            parent_relative = os.path.relpath(parent_path, tree.root_path)

            await session.run(
                """
                MERGE (f:File {path: $path})
                SET f.name = $name,
                    f.extension = $extension,
                    f.language = $language,
                    f.sizeBytes = $sizeBytes,
                    f.relativePath = $relativePath
                """,
                path=file_node.path,
                name=file_node.name,
                extension=file_node.extension,
                language=file_node.language,
                sizeBytes=file_node.size_bytes,
                relativePath=file_node.relative_path,
            )

            if parent_relative == ".":
                # File directly inside the repo root
                await session.run(
                    """
                    MATCH (r:Repository {jobId: $jobId})
                    MATCH (f:File {path: $path})
                    MERGE (r)-[:HAS_FILE]->(f)
                    """,
                    jobId=job_id,
                    path=file_node.path,
                )
            else:
                await session.run(
                    """
                    MATCH (d:Directory {path: $parentPath})
                    MATCH (f:File {path: $path})
                    MERGE (d)-[:CONTAINS]->(f)
                    """,
                    parentPath=parent_path,
                    path=file_node.path,
                )

        logger.info(
            "Graph built successfully | jobId=%s dirs=%d files=%d",
            job_id, len(tree.directories), len(tree.files),
        )
