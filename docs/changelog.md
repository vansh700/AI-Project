# Changelog

---

## Phase 1 — Development Foundation
Date: 2026-07-16

### Summary
Bootstrapped the full project scaffold across MS1, MS2, and the Frontend. No business logic implemented. Establishes the structural foundation that all future phases build upon.

### Files Created
- `docker-compose.yml`
- `.env.example`
- `ms1/package.json`
- `ms1/tsconfig.json`
- `ms1/nodemon.json`
- `ms1/.env.example`
- `ms1/src/server.ts`
- `ms1/src/app.ts`
- `ms1/src/config/logger.ts`
- `ms1/src/health/health.routes.ts`
- `ms1/src/health/health.controller.ts`
- `ms2/requirements.txt`
- `ms2/.env.example`
- `ms2/app/__init__.py`
- `ms2/app/main.py`
- `ms2/app/config/__init__.py`
- `ms2/app/config/logger.py`
- `ms2/app/health/__init__.py`
- `ms2/app/health/health_router.py`
- `ms2/app/health/health_controller.py`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`

### Files Modified
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`

### Endpoints Added
| Method | Path    | Service | Purpose          |
|--------|---------|---------|------------------|
| GET    | /health | MS1     | MS1 alive status |
| GET    | /health | MS2     | MS2 alive status |

### Database Changes
None.

### Architecture Changes
None. Scaffold matches the architecture defined in `docs/architecture.md`.

### Breaking Changes
None.

### Known Issues
None.

### Next Phase
Phase 2 — Authentication & Project Management

---

## Phase 2 — Authentication & Project Management
Date: 2026-07-16

### Summary
Implemented JWT-based authentication (register + login) and project CRUD endpoints with ownership enforcement. Set up Prisma ORM with PostgreSQL migration for User and Project tables. Added centralized Zod validation error handling.

### Files Created
- `ms1/prisma/schema.prisma`
- `ms1/prisma/migrations/20260716102235_init_users_projects/migration.sql`
- `ms1/src/config/prisma.client.ts`
- `ms1/src/types/express.d.ts`
- `ms1/src/middlewares/jwt.middleware.ts`
- `ms1/src/modules/auth/auth.routes.ts`
- `ms1/src/modules/auth/auth.controller.ts`
- `ms1/src/modules/auth/auth.service.ts`
- `ms1/src/modules/auth/auth.validation.ts`
- `ms1/src/modules/auth/user.repository.ts`
- `ms1/src/modules/project/project.routes.ts`
- `ms1/src/modules/project/project.controller.ts`
- `ms1/src/modules/project/project.service.ts`
- `ms1/src/modules/project/project.repository.ts`
- `ms1/src/modules/project/project.validation.ts`

### Files Modified
- `ms1/package.json` (added bcryptjs, jsonwebtoken, zod, prisma)
- `ms1/src/app.ts` (registered auth & project routes, improved error handler)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`

### Endpoints Added
| Method | Path           | Auth     | Purpose                     |
|--------|----------------|----------|-----------------------------|
| POST   | /auth/register | Public   | Create new user account     |
| POST   | /auth/login    | Public   | Authenticate and get token  |
| POST   | /projects      | Required | Create a new project        |
| GET    | /projects      | Required | List user's projects        |
| GET    | /projects/:id  | Required | Get single project details  |

### Database Changes
- Created `User` table (id, email, passwordHash, createdAt, updatedAt)
- Created `Project` table (id, name, repoUrl, ownerId → User FK, createdAt, updatedAt)

### Architecture Changes
None. All logic follows Controller → Service → Repository → Database flow.

### Breaking Changes
None.

### Known Issues
- No password reset or email verification
- No refresh token mechanism

### Next Phase
Phase 3 — Repository Upload & Storage

---

## Phase 3 — Repository Upload & Storage
Date: 2026-07-16

### Summary
Implemented file upload for repository zip archives. Users can upload a .zip of their repository source code to a project. The file is stored locally on disk under a structured path and the location is persisted to the Project record in the database.

### Files Created
- `ms1/src/modules/project/project-upload.service.ts`
- `ms1/src/modules/project/project-upload.controller.ts`

### Files Modified
- `ms1/package.json` (added multer, @types/multer)
- `ms1/prisma/schema.prisma` (added storagePath field to Project)
- `ms1/prisma/migrations/20260716105614_add_storage_path_to_project/migration.sql`
- `ms1/src/modules/project/project.routes.ts` (added POST /:id/upload)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`

### Endpoints Added
| Method | Path                   | Auth     | Purpose                                  |
|--------|------------------------|----------|------------------------------------------|
| POST   | /projects/:id/upload   | Required | Upload .zip archive for a project        |

### Database Changes
- Added nullable `storagePath` column to `Project` table.

### Architecture Changes
None. Upload logic follows Controller → Service → Repository → Database flow.

### Breaking Changes
None.

### Known Issues
- Storage is local filesystem — no redundancy or CDN
- No deduplication of uploads (re-upload overwrites storagePath reference but old file remains on disk)

### Next Phase
Phase 4 — Queue & Job Management

---

## Phase 5 — Repository Intelligence
Date: 2026-07-16

### Summary
Implemented the repository parsing pipeline in MS2. Workers extract uploaded zip archives, walk the file tree with language detection, build a Neo4j knowledge graph, and notify MS1 via webhook when complete.

### Files Created
- `ms2/app/config/neo4j_client.py`
- `ms2/app/parser/zip_extractor.py`
- `ms2/app/parser/language_detector.py`
- `ms2/app/parser/tree_walker.py`
- `ms2/app/graph/graph_builder.py`
- `ms2/app/services/webhook.py`
- `ms1/src/modules/webhook/webhook.controller.ts`
- `ms1/src/modules/webhook/webhook.routes.ts`
- `docs/repository_intelligence_flow.md`

### Files Modified
- `ms2/app/queue/worker.py` (full parsing pipeline)
- `ms2/app/main.py` (Neo4j driver lifecycle)
- `ms2/requirements.txt` (added neo4j, aiohttp)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`

### Endpoints Added
| Method | Path                    | Service | Purpose                          |
|--------|-------------------------|---------|----------------------------------|
| POST   | /webhooks/job-complete  | MS1     | MS2 completion callback          |

### Database Changes
None (MS1). Neo4j graph created at runtime.

### Architecture Changes
MS2 now owns Neo4j knowledge graph writes. MS2 sends webhook callbacks to MS1 after job completion.

### Breaking Changes
None.

### Known Issues
- Language detection is extension-based only
- No Neo4j indexes for performance
- Re-triggering analysis creates duplicate graphs

### Next Phase
Phase 6 — AI Planning (LangGraph)

---

## Phase 6 — AI Planning (LangGraph)
Date: 2026-07-17

### Summary
Added a LangGraph-based AI planner to MS2 that runs after the Neo4j graph is built. The planner fetches classified file context from Neo4j, generates a structured test plan via OpenAI (or a mock fallback), persists results to MS2 PostgreSQL, and sends the plan summary to MS1 via the existing webhook.

### Files Created
- `ms2/app/planner/__init__.py`
- `ms2/app/planner/coordinator.py`
- `ms2/app/planner/graph.py`
- `ms2/app/planner/state.py`
- `ms2/app/planner/nodes.py`
- `ms2/app/planner/llm_client.py`
- `ms2/app/planner/neo4j_context.py`
- `ms2/app/database/__init__.py`
- `ms2/app/database/db_client.py`
- `ms2/app/database/models.py`
- `ms2/app/database/planner_repository.py`
- `ms1/prisma/migrations/20260716195506_add_plan_summary_to_analysis_job/migration.sql`

### Files Modified
- `ms2/app/queue/worker.py` (added planner step after graph build)
- `ms2/app/main.py` (MS2 DB init on startup)
- `ms2/app/services/webhook.py` (optional planSummary in payload)
- `ms1/src/modules/webhook/webhook.controller.ts` (persist planSummary)
- `ms1/prisma/schema.prisma` (added planSummary JSON field)
- `ms2/requirements.txt` (added langgraph, langchain-openai, sqlalchemy, asyncpg)
- `ms2/.env.example` (added OPENAI_API_KEY, MS2_DB_URL)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`
- `docs/services/ms2.md`
- `docs/testing-guide.md`

### Endpoints Added
None. Existing webhook extended with optional `planSummary` field.

### Database Changes
- MS1: Added nullable `planSummary` JSONB column to `AnalysisJob` table.
- MS2: Created `planner_states` table (job_id, project_id, status, plan, error, timestamps).

### Architecture Changes
MS2 now owns a separate PostgreSQL database for planner state. LangGraph pipeline runs as step 4 in the worker after Neo4j graph build.

### Breaking Changes
None.

### Known Issues
- Mock plan used when OPENAI_API_KEY is not configured
- File classification is path-based, not AST-based
- No test execution yet (Phase 7)

### Next Phase
Phase 7 — Secure Runtime Execution

---

## Phase 7 — Secure Runtime Execution
Date: 2026-07-17

### Summary
Added Docker sandbox execution to MS2. After the AI planner generates test cases, the worker launches a locked-down container matching the repository language, validates each target file (syntax check + existence), persists results to MS2 PostgreSQL, and sends an `executionSummary` to MS1 via webhook.

### Files Created
- `ms2/app/execution/__init__.py`
- `ms2/app/execution/coordinator.py`
- `ms2/app/execution/docker_runner.py`
- `ms2/app/execution/image_selector.py`
- `ms2/app/execution/script_builder.py`
- `ms2/app/database/execution_repository.py`
- `ms1/prisma/migrations/20260717030000_add_execution_summary_to_analysis_job/migration.sql`

### Files Modified
- `ms2/app/queue/worker.py` (added Docker execution step after planner)
- `ms2/app/services/webhook.py` (optional executionSummary in payload)
- `ms2/app/database/models.py` (added ExecutionLog model)
- `ms1/src/modules/webhook/webhook.controller.ts` (persist executionSummary)
- `ms1/prisma/schema.prisma` (added executionSummary JSON field)
- `ms2/requirements.txt` (added docker SDK)
- `ms2/.env.example` (added Docker execution config)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`
- `docs/services/ms2.md`
- `docs/testing-guide.md`
- `docs/repository_intelligence_flow.md`

### Endpoints Added
None. Existing webhook extended with optional `executionSummary` field.

### Database Changes
- MS1: Added nullable `executionSummary` JSONB column to `AnalysisJob` table.
- MS2: Created `execution_logs` table (job_id, project_id, status, summary, error, timestamps).

### Architecture Changes
MS2 worker pipeline now includes step 5: Docker sandbox execution after AI planning. Containers run with no network, read-only filesystem, memory/CPU limits, and dropped capabilities.

### Breaking Changes
None.

### Known Issues
- Execution performs syntax/file checks only — not full test suite runs
- Mock execution used when Docker daemon is unavailable
- Docker Desktop must be running on the host machine

### Next Phase
Phase 8 — Dynamic Security Testing

---

## Phase 8 — Dynamic Security Testing
Date: 2026-07-17

### Summary
Added dynamic security scanning to MS2. After Docker execution, the worker runs pattern-based vulnerability detection, sensitive file checks, and auth-coverage probes across the repository. Findings are persisted to MS2 PostgreSQL and sent to MS1 as `securitySummary` via webhook.

### Files Created
- `ms2/app/security/__init__.py`
- `ms2/app/security/coordinator.py`
- `ms2/app/security/rule_engine.py`
- `ms2/app/security/pattern_scanner.py`
- `ms2/app/security/sensitive_file_scanner.py`
- `ms2/app/security/auth_probe.py`
- `ms2/app/database/security_repository.py`
- `ms1/prisma/migrations/20260717040000_add_security_summary_to_analysis_job/migration.sql`

### Files Modified
- `ms2/app/queue/worker.py` (added security scan step after Docker execution)
- `ms2/app/services/webhook.py` (optional securitySummary in payload)
- `ms2/app/database/models.py` (added SecurityLog model)
- `ms1/src/modules/webhook/webhook.controller.ts` (persist securitySummary)
- `ms1/prisma/schema.prisma` (added securitySummary JSON field)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`
- `docs/services/ms2.md`
- `docs/testing-guide.md`
- `docs/repository_intelligence_flow.md`

### Endpoints Added
None. Existing webhook extended with optional `securitySummary` field.

### Database Changes
- MS1: Added nullable `securitySummary` JSONB column to `AnalysisJob` table.
- MS2: Created `security_logs` table (job_id, project_id, status, summary, error, timestamps).

### Architecture Changes
MS2 worker pipeline now includes step 6: dynamic security scanning after Docker execution. Three scan types run: pattern rules, sensitive file detection, and auth coverage probes.

### Breaking Changes
None.

### Known Issues
- Security scanning is heuristic/pattern-based — not a full SAST/DAST tool
- Auth probe may flag public routes that intentionally lack auth
- Pattern rules may produce false positives on test fixtures

### Next Phase
Phase 9 — Reports & Real-Time Frontend

---

## Phase 9 — Reports & Real-Time Frontend
Date: 2026-07-17

### Summary
Added unified report generation on MS1, WebSocket real-time job updates, new report API endpoints, and a React frontend for login, project management, live job tracking, and report viewing.

### Files Created
- `ms1/src/modules/report/report.service.ts`
- `ms1/src/modules/websocket/websocket.gateway.ts`
- `ms1/prisma/migrations/20260717050000_add_report_summary_to_analysis_job/migration.sql`
- `frontend/src/api/client.ts`
- `frontend/src/api/auth.api.ts`
- `frontend/src/api/project.api.ts`
- `frontend/src/api/analysis.api.ts`
- `frontend/src/types/api.types.ts`
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/hooks/useJobSocket.ts`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/ProjectPage.tsx`
- `frontend/src/components/JobStatusBadge.tsx`
- `frontend/src/components/ReportView.tsx`
- `frontend/src/index.css`

### Files Modified
- `ms1/src/server.ts` (HTTP server + WebSocket on `/ws`)
- `ms1/src/modules/analysis/analysis.service.ts` (report endpoints, WebSocket emit on trigger)
- `ms1/src/modules/analysis/analysis.controller.ts` (getJobById, getReport)
- `ms1/src/modules/analysis/analysis.routes.ts` (GET /:jobId, GET /:jobId/report)
- `ms1/src/modules/analysis/analysis.repository.ts` (findJobById)
- `ms1/src/modules/webhook/webhook.controller.ts` (build reportSummary, emit WebSocket)
- `ms1/prisma/schema.prisma` (added reportSummary JSON field)
- `ms1/package.json` (added ws)
- `ms2/app/queue/worker.py` (RUNNING webhook at job start)
- `ms2/app/services/webhook.py` (notify_job_running)
- `frontend/src/App.tsx` (full UI replacing placeholder)
- `frontend/src/main.tsx` (import index.css)
- `frontend/vite.config.ts` (WebSocket proxy)
- `docs/current-phase.md`
- `docs/changelog.md`
- `docs/file-index.md`
- `docs/services/ms1.md`
- `docs/services/frontend.md`
- `docs/api/api-refrence.md`
- `docs/queue/queue-flow.md`
- `docs/workflow/workflow-refrence.md`
- `docs/testing-guide.md`

### Endpoints Added
| Method | Path | Service | Purpose |
|--------|------|---------|---------|
| GET | `/projects/:id/analysis/:jobId` | MS1 | Get single analysis job |
| GET | `/projects/:id/analysis/:jobId/report` | MS1 | Get unified report |
| WS | `/ws?token=<JWT>` | MS1 | Real-time job updates |

### Database Changes
- MS1: Added nullable `reportSummary` JSONB column to `AnalysisJob` table.

### Architecture Changes
MS1 now serves WebSocket connections for real-time job status. Report is compiled on webhook COMPLETED from plan + execution + security summaries. React frontend consumes MS1 REST + WebSocket via Vite proxy.

### Breaking Changes
None.

### Known Issues
- WebSocket only pushes on job create and webhook events (no per-step progress from MS2)
- Frontend has no react-router — uses in-app view state
- Report test plan section shows raw JSON

### Next Phase
Phase 10 — Production Hardening