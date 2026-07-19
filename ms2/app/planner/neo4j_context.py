"""Neo4j subgraph query and Python classification for the AI planner context.

Fetches files belonging to the repository using the jobId and classifies
them based on names/paths to determine Endpoints, Controllers, Services,
Middlewares, Models, Authentication, and BusinessRules.
"""
import os
from app.config.neo4j_client import get_driver
from app.config.logger import get_logger

logger = get_logger("ms2.planner.neo4j_context")

RELEVANT_LABELS = {
    "Endpoint",
    "Controller",
    "Service",
    "Middleware",
    "Model",
    "Authentication",
    "BusinessRule",
}


def classify_file(relative_path: str) -> list[str]:
    """Classify a file path into virtual architectural labels."""
    labels = ["File"]
    path_lower = relative_path.lower().replace("\\", "/")
    
    if "controller" in path_lower:
        labels.append("Controller")
    if "service" in path_lower:
        labels.append("Service")
    if "route" in path_lower or "endpoint" in path_lower or "/api/" in path_lower:
        labels.append("Endpoint")
    if "model" in path_lower or "schema" in path_lower or "entity" in path_lower:
        labels.append("Model")
    if "middleware" in path_lower:
        labels.append("Middleware")
    if "auth" in path_lower or "jwt" in path_lower:
        labels.append("Authentication")
    if "rule" in path_lower or "validation" in path_lower or "policy" in path_lower:
        labels.append("BusinessRule")
        
    return labels


async def fetch_relevant_subgraph(job_id: str) -> dict:
    """Return a structured dict of classified files from Neo4j for a given jobId."""
    driver = get_driver()
    
    # 1. Fetch the Repository rootPath
    async with driver.session() as session:
        result = await session.run(
            "MATCH (r:Repository {jobId: $jobId}) RETURN r.rootPath AS rootPath",
            jobId=job_id
        )
        record = await result.single()
        if not record:
            logger.warning("No Repository found in Neo4j for jobId=%s", job_id)
            return {"nodes": [], "total": 0}
        root_path = record["rootPath"]

    # 2. Fetch all Files belonging to that rootPath
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (f:File)
            WHERE f.path STARTS WITH $rootPath
            RETURN
                f.path         AS path,
                f.name         AS name,
                f.language     AS language,
                f.sizeBytes    AS sizeBytes,
                f.relativePath AS relativePath
            ORDER BY f.relativePath
            """,
            rootPath=root_path
        )
        records = await result.data()

    # 3. Classify files and filter for relevant architectural nodes
    all_nodes = []
    relevant_nodes = []
    
    for r in records:
        rel_path = r["relativePath"]
        labels = classify_file(rel_path)
        node = {
            "labels": labels,
            "path": rel_path,
            "name": r["name"],
            "language": r["language"],
            "size": r["sizeBytes"]
        }
        all_nodes.append(node)
        
        # Check if the node matches any of our target architectural labels
        if any(label in RELEVANT_LABELS for label in labels):
            relevant_nodes.append(node)

    # Fallback to all files if no specific architectural labels match
    selected_nodes = relevant_nodes if relevant_nodes else all_nodes
    # Limit nodes to avoid overloading token limits
    selected_nodes = selected_nodes[:150]

    logger.info(
        "Neo4j context classified | jobId=%s total_files=%d selected_files=%d",
        job_id, len(records), len(selected_nodes)
    )
    
    return {
        "nodes": selected_nodes,
        "total": len(selected_nodes)
    }
