# File Index

Every file in the project is registered here. No exceptions.

---

## Phase 1 — Development Foundation

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `docker-compose.yml` | Phase 1 | Defines all infrastructure services | — | — | — | — | YES |
| `.env.example` | Phase 1 | Root env template for Docker Compose | — | — | — | — | YES |
| `ms1/package.json` | Phase 1 | MS1 npm manifest and scripts | — | — | — | — | YES |
| `ms1/tsconfig.json` | Phase 1 | MS1 TypeScript compiler config | — | — | — | — | YES |
| `ms1/nodemon.json` | Phase 1 | MS1 dev server watch config | — | — | — | — | YES |
| `ms1/.env.example` | Phase 1 | MS1 environment variable template | — | — | — | — | YES |
| `ms1/src/server.ts` | Phase 1 | MS1 HTTP server bootstrap | — | `app.ts`, `logger.ts` | — | — | LOW RISK |
| `ms1/src/app.ts` | Phase 1 | Express app wiring, middleware, error handlers | `server.ts` | `health.routes.ts`, `logger.ts` | `app` | — | LOW RISK |
| `ms1/src/config/logger.ts` | Phase 1 | Centralized Winston logger instance | All MS1 modules | `winston` | `logger` | — | LOW RISK |
| `ms1/src/health/health.routes.ts` | Phase 1 | Health route registration | `app.ts` | `health.controller.ts` | `healthRoutes` | GET /health | YES |
| `ms1/src/health/health.controller.ts` | Phase 1 | Health check endpoint handler | `health.routes.ts` | — | `getHealth` | GET /health | YES |
| `ms2/requirements.txt` | Phase 1 | MS2 Python dependency manifest | — | — | — | — | YES |
| `ms2/.env.example` | Phase 1 | MS2 environment variable template | — | — | — | — | YES |
| `ms2/app/__init__.py` | Phase 1 | Python package marker | — | — | — | — | NO |
| `ms2/app/main.py` | Phase 1 | FastAPI app instance and startup | — | `health_router.py`, `logger.py` | `app` | — | LOW RISK |
| `ms2/app/config/__init__.py` | Phase 1 | Python package marker | — | — | — | — | NO |
| `ms2/app/config/logger.py` | Phase 1 | Centralized Python logger factory | All MS2 modules | `logging` | `get_logger` | — | LOW RISK |
| `ms2/app/health/__init__.py` | Phase 1 | Python package marker | — | — | — | — | NO |
| `ms2/app/health/health_router.py` | Phase 1 | Health route registration | `main.py` | `health_controller.py` | `router` | GET /health | YES |
| `ms2/app/health/health_controller.py` | Phase 1 | Health check response builder | `health_router.py` | — | `get_health_response` | GET /health | YES |
| `frontend/package.json` | Phase 1 | Frontend npm manifest and scripts | — | — | — | — | YES |
| `frontend/tsconfig.json` | Phase 1 | Frontend TypeScript compiler config | — | — | — | — | YES |
| `frontend/tsconfig.node.json` | Phase 1 | TypeScript config for vite.config.ts | `tsconfig.json` | — | — | — | YES |
| `frontend/vite.config.ts` | Phase 1 | Vite dev server config with /api proxy | — | — | — | — | LOW RISK |
| `frontend/index.html` | Phase 1 | HTML shell for React app | — | — | — | — | YES |
| `frontend/src/main.tsx` | Phase 1 | React app entry point | — | `App.tsx` | — | — | LOW RISK |
| `frontend/src/App.tsx` | Phase 1 | Root React component (placeholder) | `main.tsx` | — | `App` | — | YES |

---

## Phase 2 — Authentication & Project Management

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms1/prisma/schema.prisma` | Phase 2 | Database schema (User, Project) | Prisma CLI | — | — | — | LOW RISK |
| `ms1/src/config/prisma.client.ts` | Phase 2 | Prisma singleton instance | All repositories | `@prisma/client` | `prisma` | — | LOW RISK |
| `ms1/src/types/express.d.ts` | Phase 2 | Adds userId to Express Request type | TypeScript compiler | — | — | — | LOW RISK |
| `ms1/src/middlewares/jwt.middleware.ts` | Phase 2 | JWT Bearer token verification | `project.routes.ts` | `jsonwebtoken` | `authenticate` | — | LOW RISK |
| `ms1/src/modules/auth/auth.routes.ts` | Phase 2 | Auth route registration | `app.ts` | `auth.controller.ts` | `authRoutes` | POST /auth/* | YES |
| `ms1/src/modules/auth/auth.controller.ts` | Phase 2 | Auth request handler | `auth.routes.ts` | `auth.service.ts`, `auth.validation.ts` | `register`, `login` | POST /auth/* | YES |
| `ms1/src/modules/auth/auth.service.ts` | Phase 2 | Auth business logic (hash, JWT) | `auth.controller.ts` | `user.repository.ts`, `bcryptjs`, `jsonwebtoken` | `registerUser`, `loginUser` | — | LOW RISK |
| `ms1/src/modules/auth/auth.validation.ts` | Phase 2 | Zod schemas for auth input | `auth.controller.ts` | `zod` | `registerSchema`, `loginSchema` | — | YES |
| `ms1/src/modules/auth/user.repository.ts` | Phase 2 | User table CRUD | `auth.service.ts` | `prisma.client.ts` | `findUserByEmail`, `createUser` | — | YES |
| `ms1/src/modules/project/project.routes.ts` | Phase 2 | Project route registration | `app.ts` | `jwt.middleware.ts`, `project.controller.ts` | `projectRoutes` | /projects/* | YES |
| `ms1/src/modules/project/project.controller.ts` | Phase 2 | Project request handler | `project.routes.ts` | `project.service.ts`, `project.validation.ts` | `create`, `list`, `getById` | /projects/* | YES |
| `ms1/src/modules/project/project.service.ts` | Phase 2 | Project business logic & ownership | `project.controller.ts` | `project.repository.ts` | `createNewProject`, `getProjectsForUser`, `getProjectDetail` | — | LOW RISK |
| `ms1/src/modules/project/project.repository.ts` | Phase 2 | Project table CRUD | `project.service.ts` | `prisma.client.ts` | `createProject`, `findProjectsByOwner`, `findProjectById` | — | YES |
| `ms1/src/modules/project/project.validation.ts` | Phase 2 | Zod schema for project input | `project.controller.ts` | `zod` | `createProjectSchema` | — | YES |

---

## Phase 3 — Repository Upload & Storage

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms1/src/modules/project/project-upload.service.ts` | Phase 3 | Moves uploaded file to structured storage dir and updates DB | `project-upload.controller.ts` | `prisma.client.ts`, `fs`, `path` | `saveUploadedFile` | — | LOW RISK |
| `ms1/src/modules/project/project-upload.controller.ts` | Phase 3 | Handles multipart upload, enforces ownership, calls upload service | `project.routes.ts` | `project.service.ts`, `project-upload.service.ts`, `multer` | `uploadMiddleware`, `uploadRepository` | POST /projects/:id/upload | YES |
| `docs/testing-guide.md` | Phase 3 | Centralized line-by-line verification script for all phases | — | — | — | — | YES |

---

## Phase 4 — Queue & Job Management

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms1/src/config/queue.ts` | Phase 4 | BullMQ queue singleton connected to Redis | `analysis.service.ts` | `bullmq`, `ioredis` | `analysisQueue` | — | YES |
| `ms1/src/modules/analysis/analysis.repository.ts` | Phase 4 | DB CRUD operations for the AnalysisJob table | `analysis.service.ts` | `prisma.client.ts` | `createAnalysisJob`, `findJobsByProject` | — | YES |
| `ms1/src/modules/analysis/analysis.service.ts` | Phase 4 | Business logic to trigger & fetch analysis jobs | `analysis.controller.ts` | `analysis.repository.ts`, `queue.ts` | `triggerAnalysis`, `getAnalysisJobs` | — | LOW RISK |
| `ms1/src/modules/analysis/analysis.controller.ts` | Phase 4 | HTTP handlers for analysis triggers & lists | `analysis.routes.ts` | `analysis.service.ts` | `startAnalysis`, `listAnalysisJobs` | — | YES |
| `ms1/src/modules/analysis/analysis.routes.ts` | Phase 4 | Route registration for project analysis | `app.ts` | `analysis.controller.ts` | `analysisRoutes` | /projects/:id/analysis | YES |
| `ms2/app/queue/worker.py` | Phase 4 | Python BullMQ worker executing background tasks | `main.py` | `bullmq`, `logger` | `create_worker` | — | YES |

---

## Phase 5 — Repository Intelligence

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms2/app/config/neo4j_client.py` | Phase 5 | Neo4j async database driver singleton | `graph_builder.py`, `main.py` | `neo4j` | `get_driver`, `close_driver` | — | YES |
| `ms2/app/parser/zip_extractor.py` | Phase 5 | Extracts uploaded zip archives to OS temp directory | `worker.py` | `zipfile`, `tempfile` | `extract_zip` | — | YES |
| `ms2/app/parser/language_detector.py` | Phase 5 | Map file extension to programming language | `tree_walker.py` | `os` | `detect_language` | — | YES |
| `ms2/app/parser/tree_walker.py` | Phase 5 | Walk extracted repository files skipping ignored dirs | `worker.py` | `language_detector.py` | `walk_repository`, `RepositoryTree` | — | YES |
| `ms2/app/graph/graph_builder.py` | Phase 5 | Persist walked repo files/dirs to Neo4j graph | `worker.py` | `neo4j_client.py` | `build_graph` | — | YES |
| `ms2/app/services/webhook.py` | Phase 5 | Sends async completion callbacks back to MS1 | `worker.py` | `aiohttp` | `notify_job_complete`, `notify_job_failed` | — | YES |
| `ms1/src/modules/webhook/webhook.controller.ts` | Phase 5 | MS1 handler processing MS2 status callback webhooks | `webhook.routes.ts` | `prisma.client.ts` | `handleJobComplete` | POST /webhooks/job-complete | YES |
| `ms1/src/modules/webhook/webhook.routes.ts` | Phase 5 | Webhook router registration | `app.ts` | `webhook.controller.ts` | `webhookRoutes` | /webhooks/* | YES |

---

## Phase 6 — AI Planning (LangGraph)

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms2/app/planner/__init__.py` | Phase 6 | Python package marker | — | — | — | — | NO |
| `ms2/app/planner/coordinator.py` | Phase 6 | Entry point — runs LangGraph and persists plan | `worker.py` | `graph.py`, `planner_repository.py` | `run_planner` | — | LOW RISK |
| `ms2/app/planner/graph.py` | Phase 6 | LangGraph StateGraph assembly (intake→context→plan→reflect) | `coordinator.py` | `nodes.py`, `state.py` | `get_planner_graph` | — | LOW RISK |
| `ms2/app/planner/state.py` | Phase 6 | TypedDict schema for shared planner graph state | `graph.py`, `nodes.py` | — | `PlannerAgentState` | — | YES |
| `ms2/app/planner/nodes.py` | Phase 6 | LangGraph node functions (intake, context, plan, reflect) | `graph.py` | `neo4j_context.py`, `llm_client.py` | `intake_node`, `context_node`, `plan_node`, `reflect_node` | — | LOW RISK |
| `ms2/app/planner/llm_client.py` | Phase 6 | OpenAI ChatOpenAI singleton (gpt-4.1 / gpt-4o fallback) | `nodes.py` | `langchain-openai` | `get_llm`, `get_fallback_llm` | — | YES |
| `ms2/app/planner/neo4j_context.py` | Phase 6 | Fetch and classify Neo4j file nodes for planner context | `nodes.py` | `neo4j_client.py` | `fetch_relevant_subgraph`, `classify_file` | — | YES |
| `ms2/app/database/__init__.py` | Phase 6 | Python package marker | — | — | — | — | NO |
| `ms2/app/database/db_client.py` | Phase 6 | Async SQLAlchemy engine and session factory for MS2 DB | `planner_repository.py`, `main.py` | `sqlalchemy`, `asyncpg` | `get_session`, `create_tables`, `close_engine` | — | LOW RISK |
| `ms2/app/database/models.py` | Phase 6 | SQLAlchemy ORM model for planner state | `planner_repository.py`, `db_client.py` | `sqlalchemy` | `PlannerState`, `Base` | — | YES |
| `ms2/app/database/planner_repository.py` | Phase 6 | CRUD for PlannerState records | `coordinator.py` | `db_client.py`, `models.py` | `save_plan`, `mark_plan_failed`, `get_plan_by_job_id` | — | YES |
| `ms1/prisma/migrations/20260716195506_add_plan_summary_to_analysis_job/migration.sql` | Phase 6 | Adds planSummary JSONB column to AnalysisJob | Prisma CLI | — | — | — | NO |

---

## Phase 7 — Secure Runtime Execution

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms2/app/execution/__init__.py` | Phase 7 | Python package marker | — | — | — | — | NO |
| `ms2/app/execution/coordinator.py` | Phase 7 | Entry point — runs Docker sandbox and persists results | `worker.py` | `docker_runner.py`, `execution_repository.py` | `run_execution` | — | LOW RISK |
| `ms2/app/execution/docker_runner.py` | Phase 7 | Launches locked-down Docker containers for test validation | `coordinator.py` | `image_selector.py`, `script_builder.py`, `docker` | `run_sandbox`, `is_docker_available` | — | LOW RISK |
| `ms2/app/execution/image_selector.py` | Phase 7 | Maps repository language to sandbox Docker image | `docker_runner.py` | — | `get_sandbox_image` | — | YES |
| `ms2/app/execution/script_builder.py` | Phase 7 | Generates shell validation script for sandbox container | `docker_runner.py` | — | `build_validation_script` | — | YES |
| `ms2/app/database/execution_repository.py` | Phase 7 | CRUD for ExecutionLog records | `coordinator.py` | `db_client.py`, `models.py` | `save_execution`, `mark_execution_failed`, `get_execution_by_job_id` | — | YES |
| `ms1/prisma/migrations/20260717030000_add_execution_summary_to_analysis_job/migration.sql` | Phase 7 | Adds executionSummary JSONB column to AnalysisJob | Prisma CLI | — | — | — | NO |

---

## Phase 8 — Dynamic Security Testing

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms2/app/security/__init__.py` | Phase 8 | Python package marker | — | — | — | — | NO |
| `ms2/app/security/coordinator.py` | Phase 8 | Entry point — runs security scans and persists findings | `worker.py` | `pattern_scanner.py`, `sensitive_file_scanner.py`, `auth_probe.py`, `security_repository.py` | `run_security_scan` | — | LOW RISK |
| `ms2/app/security/rule_engine.py` | Phase 8 | Security rule definitions (secrets, SQLi, eval, CORS, JWT) | `pattern_scanner.py`, `sensitive_file_scanner.py` | — | `RULES`, `SENSITIVE_FILES`, `SecurityRule` | — | YES |
| `ms2/app/security/pattern_scanner.py` | Phase 8 | Static pattern-based vulnerability scanner | `coordinator.py` | `rule_engine.py` | `scan_files` | — | YES |
| `ms2/app/security/sensitive_file_scanner.py` | Phase 8 | Detects committed sensitive files (.env, keys) | `coordinator.py` | `rule_engine.py` | `scan_sensitive_files` | — | YES |
| `ms2/app/security/auth_probe.py` | Phase 8 | Dynamic auth-coverage probe for route/controller files | `coordinator.py` | — | `probe_auth_coverage` | — | YES |
| `ms2/app/database/security_repository.py` | Phase 8 | CRUD for SecurityLog records | `coordinator.py` | `db_client.py`, `models.py` | `save_security_scan`, `mark_security_failed`, `get_security_by_job_id` | — | YES |
| `ms1/prisma/migrations/20260717040000_add_security_summary_to_analysis_job/migration.sql` | Phase 8 | Adds securitySummary JSONB column to AnalysisJob | Prisma CLI | — | — | — | NO |

---

## Phase 9 — Reports & Real-Time Frontend

| File | Created | Purpose | Imported By | Depends On | Exports | Related APIs | Safe To Modify |
|------|---------|---------|-------------|------------|---------|--------------|----------------|
| `ms1/src/modules/report/report.service.ts` | Phase 9 | Builds unified reportSummary from job summaries | `analysis.service.ts`, `webhook.controller.ts` | — | `buildReportSummary`, `ReportSummary` | GET /projects/:id/analysis/:jobId/report | YES |
| `ms1/src/modules/websocket/websocket.gateway.ts` | Phase 9 | WebSocket server and job update emitter | `server.ts`, `analysis.service.ts`, `webhook.controller.ts` | `ws`, `jsonwebtoken` | `initWebSocket`, `emitJobUpdate` | WS /ws | LOW RISK |
| `ms1/prisma/migrations/20260717050000_add_report_summary_to_analysis_job/migration.sql` | Phase 9 | Adds reportSummary JSONB column to AnalysisJob | Prisma CLI | — | — | — | NO |
| `frontend/src/api/client.ts` | Phase 9 | Base fetch wrapper with JWT auth | All frontend API modules | — | `apiFetch`, `getToken`, `setToken` | — | YES |
| `frontend/src/api/auth.api.ts` | Phase 9 | Login/register API calls | `LoginPage.tsx` | `client.ts` | `login`, `register` | POST /auth/* | YES |
| `frontend/src/api/project.api.ts` | Phase 9 | Project CRUD and upload API calls | `DashboardPage.tsx`, `ProjectPage.tsx` | `client.ts` | `listProjects`, `createProject`, `getProject`, `uploadRepository` | /projects/* | YES |
| `frontend/src/api/analysis.api.ts` | Phase 9 | Analysis trigger, list, report API calls | `ProjectPage.tsx` | `client.ts` | `listJobs`, `triggerAnalysis`, `getJob`, `getReport` | /projects/:id/analysis/* | YES |
| `frontend/src/types/api.types.ts` | Phase 9 | Shared TypeScript types for API responses | Frontend pages/components | — | `Project`, `AnalysisJob`, `ReportSummary` | — | YES |
| `frontend/src/context/AuthContext.tsx` | Phase 9 | Auth state provider | `App.tsx`, pages | `client.ts` | `AuthProvider`, `useAuth` | — | YES |
| `frontend/src/hooks/useJobSocket.ts` | Phase 9 | WebSocket hook for real-time job updates | `ProjectPage.tsx` | — | `useJobSocket` | WS /ws | YES |
| `frontend/src/pages/LoginPage.tsx` | Phase 9 | Login/register screen | `App.tsx` | `auth.api.ts` | `LoginPage` | — | YES |
| `frontend/src/pages/DashboardPage.tsx` | Phase 9 | Project list and create screen | `App.tsx` | `project.api.ts` | `DashboardPage` | — | YES |
| `frontend/src/pages/ProjectPage.tsx` | Phase 9 | Upload, analyze, live status, report view | `App.tsx` | `project.api.ts`, `analysis.api.ts`, `useJobSocket` | `ProjectPage` | — | YES |
| `frontend/src/components/JobStatusBadge.tsx` | Phase 9 | Colored status badge for jobs | `ProjectPage.tsx`, `ReportView.tsx` | — | `JobStatusBadge` | — | YES |
| `frontend/src/components/ReportView.tsx` | Phase 9 | Renders unified analysis report | `ProjectPage.tsx` | — | `ReportView` | — | YES |
| `frontend/src/index.css` | Phase 9 | Global styles for frontend UI | `main.tsx` | — | — | — | YES |