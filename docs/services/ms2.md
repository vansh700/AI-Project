# MS2 — Worker Pool & AI Execution

MS2 is a FastAPI worker service that consumes analysis jobs from BullMQ, parses repositories, builds the Neo4j knowledge graph, runs the AI planner, executes tests in a Docker sandbox, performs dynamic security scanning, and notifies MS1 on completion.

---

## Worker

**Purpose**: Consumes jobs from the `analysis-queue` BullMQ queue and orchestrates the full analysis pipeline.

**Dependencies**: Redis, Neo4j, MS2 PostgreSQL, Docker, MS1 webhook endpoint.

**Input**: BullMQ job payload `{ jobId, projectId, storagePath }`.

**Output**: Neo4j graph, planner state, execution logs, security findings in MS2 DB, webhook callback to MS1 with optional `planSummary`, `executionSummary`, and `securitySummary`.

**Failure conditions**: Missing zip file, extraction failure, Neo4j connection error, unhandled exception during pipeline. Planner, execution, and security failures are logged but do not fail the overall job.

**Pipeline order**: extract → walk → build graph → AI planner → Docker execution → security scan → webhook

---

## Parser

**Purpose**: Extracts uploaded zip archives and walks the repository file tree.

**Dependencies**: OS temp directory, `language_detector`.

**Input**: Absolute path to a `.zip` file on disk.

**Output**: `RepositoryTree` with directories and files (language, size, relative path).

**Failure conditions**: Corrupt zip, unreadable storage path.

---

## Knowledge Graph

**Purpose**: Persists repository structure in Neo4j as `Repository → Directory → File` nodes.

**Dependencies**: Neo4j async driver (`neo4j_client`).

**Input**: `jobId`, `projectId`, `RepositoryTree`.

**Output**: Neo4j graph nodes and relationships keyed by `jobId`.

**Failure conditions**: Neo4j unavailable, write transaction failure.

---

## Planner

**Purpose**: Generates a structured AI test plan from repository context using LangGraph.

**Dependencies**: Neo4j (subgraph context), OpenAI API (optional), MS2 PostgreSQL.

**Input**: `{ jobId, projectId, repositoryPath, language, framework }`.

**Output**: JSON test plan with `summary`, `testCases`, and `coverage` metrics. Persisted to `planner_states` table and forwarded to MS1 as `planSummary`.

**Failure conditions**: LLM API error (falls back to mock plan if no API key), Neo4j context fetch failure, JSON parse error from LLM response.

---

## LangGraph

**Purpose**: Orchestrates the planner as a linear state machine.

**Graph order**: `intake → context → plan → reflect → END`

**State fields**: `analysisId`, `repositoryPath`, `language`, `framework`, `graph`, `plan`, `testCases`, `executionResults`, `findings`, `report`.

**Dependencies**: `langgraph`, `langchain-openai`, planner nodes.

---

## Reflection

**Purpose**: Validates generated test cases in the `reflect_node` — ensures required fields exist and warns on low coverage.

**Dependencies**: Plan output from `plan_node`.

**Input**: Raw plan JSON from LLM.

**Output**: Validated `testCases` list written back to graph state.

**Failure conditions**: None blocking — malformed test cases are skipped with a warning.

---

## Docker

**Purpose**: Launches sandboxed containers to validate test-case targets from the AI plan.

**Dependencies**: Docker daemon, `docker` Python SDK, language-specific images (node, python, golang, temurin).

**Input**: Repository path, language, list of test cases from planner.

**Output**: Execution summary with per-test results (passed/failed/skipped). Persisted to `execution_logs` table and forwarded to MS1 as `executionSummary`.

**Security constraints**:
- `--network none` — no outbound network
- `--read-only` root filesystem with tmpfs for `/tmp`
- Memory limit (default 256m) and CPU quota
- `--cap-drop ALL` and `no-new-privileges`
- Repository mounted read-only at `/repo`
- Container timeout (default 120s)

**Failure conditions**: Docker daemon unavailable (falls back to mock/skipped results), container timeout, image pull failure.

**Environment variables**: `DOCKER_ENABLED`, `EXECUTION_TIMEOUT_SECONDS`, `EXECUTION_MEMORY_LIMIT`, `EXECUTION_CPU_QUOTA`

---

## Execution

**Purpose**: Coordinates sandbox test validation after AI planning.

**Dependencies**: `docker_runner`, `execution_repository`.

**Input**: `{ jobId, projectId, repositoryPath, language, framework, testCases }`.

**Output**: `executionSummary` dict with `totalTests`, `passed`, `failed`, `results[]`.

**Validation per test case**:
- JavaScript/TypeScript: `node --check` syntax validation
- Python: `python3 -m py_compile` syntax validation
- Other languages: file existence check only

---

## Security

**Purpose**: Runs dynamic security scanning across the repository after test execution.

**Dependencies**: Repository file tree from parser, `security_repository`.

**Input**: `{ jobId, projectId, files[], language, framework }`.

**Output**: `securitySummary` dict with severity counts and `findings[]`. Persisted to `security_logs` table and forwarded to MS1.

**Scan types**:
1. **Pattern scanner** — regex rules for hardcoded secrets, SQL injection, eval/exec, weak crypto, CORS wildcard, debug mode, JWT none algorithm
2. **Sensitive file scanner** — detects committed `.env`, SSH keys, credential files
3. **Auth probe** — flags route/controller files with no auth middleware references

**Failure conditions**: Scan errors are logged but do not fail the overall job.

---
