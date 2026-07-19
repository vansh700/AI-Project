# Current Phase

Current Milestone: 9
Name: Reports & Real-Time Frontend
Status: Completed
Completion Date: 2026-07-17
Next Phase: 10 — Production Hardening
Overall Progress: 9 / 10

---

## Completed Features

- User registration & login with JWT
- Project CRUD (create, list, get by ID)
- Repository zip upload (local storage)
- BullMQ async job dispatch (MS1 → Redis → MS2)
- AnalysisJob lifecycle tracking in MS1 DB
- Repository zip extraction to OS temp directory
- File tree walking with language detection
- Neo4j knowledge graph (Repository → Directories → Files)
- MS2 → MS1 webhook for job status updates (COMPLETED / FAILED / RUNNING)
- AnalysisJob status updated in MS1 DB after worker completion
- LangGraph AI planner pipeline (intake → context → plan → reflect)
- Neo4j subgraph fetch and file classification for planner context
- OpenAI LLM test plan generation with gpt-4.1 / gpt-4o fallback
- Mock test plan fallback when OPENAI_API_KEY is not configured
- Planner state persistence in MS2 PostgreSQL (`planner_states` table)
- `planSummary` JSON stored on AnalysisJob via webhook callback
- Docker sandbox execution of generated test cases
- Language-specific sandbox images (Node, Python, Go, Java)
- Secure container constraints (no network, read-only FS, memory/CPU limits)
- Syntax validation and file-existence checks per test case
- Execution results persisted in MS2 PostgreSQL (`execution_logs` table)
- `executionSummary` JSON stored on AnalysisJob via webhook callback
- Dynamic security scanning (pattern, sensitive file, auth probe)
- Security rules for secrets, SQL injection, eval, weak crypto, CORS, JWT
- Sensitive file detection (.env, keys, credentials)
- Auth coverage probe for route/controller files
- Security findings persisted in MS2 PostgreSQL (`security_logs` table)
- `securitySummary` JSON stored on AnalysisJob via webhook callback
- Unified report generation from plan + execution + security summaries
- `reportSummary` JSON stored on AnalysisJob when job completes
- WebSocket real-time job updates (`/ws?token=...`)
- GET single job and GET report endpoints
- React frontend: login, dashboard, project view, live job status, report viewer

## Pending Features

- Production hardening (Phase 10)

## Known Limitations

- Language detection is extension-based only (no AST analysis yet)
- No Neo4j indexes created yet (will be needed for performance in later phases)
- No deduplication: re-triggering analysis creates a new graph for the same jobId
- Execution runs syntax/file checks only — not full test suite execution
- Security scanning is pattern/heuristic-based — not a full SAST/DAST tool
- WebSocket emits on job create and webhook update only — no per-step MS2 progress
- Frontend uses simple view-state navigation (no react-router)
- Mock execution used when Docker daemon is unavailable or DOCKER_ENABLED=false
- Mock plan is used automatically when OPENAI_API_KEY is missing or is a placeholder
