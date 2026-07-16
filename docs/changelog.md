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