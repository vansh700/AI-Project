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