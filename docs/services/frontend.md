# Frontend — React Application

The React frontend is the user-facing interface for the AI Code Analyst platform. It communicates exclusively with MS1 via REST and WebSocket — never with MS2 directly.

---

## Pages

### LoginPage
**Purpose**: User authentication (login and register).

**API calls**: `POST /auth/login`, `POST /auth/register`

**Flow**: User enters credentials → token stored in localStorage → AuthContext updated → Dashboard shown.

### DashboardPage
**Purpose**: List and create projects.

**API calls**: `GET /projects`, `POST /projects`

**Flow**: Shows project cards → click project → navigate to ProjectPage.

### ProjectPage
**Purpose**: Upload repository, trigger analysis, watch live status, view reports.

**API calls**:
- `GET /projects/:id`
- `POST /projects/:id/upload`
- `POST /projects/:id/analysis`
- `GET /projects/:id/analysis`
- `GET /projects/:id/analysis/:jobId/report`

**WebSocket**: Connects to `/ws?token=<JWT>` for real-time `job_updated` events.

**Flow**: Upload zip → Run Analysis → job appears as QUEUED → updates to RUNNING via WebSocket → COMPLETED with report viewer.

---

## Components

| Component | Purpose |
|-----------|---------|
| `JobStatusBadge` | Color-coded job status (QUEUED, RUNNING, COMPLETED, FAILED) |
| `ReportView` | Displays unified report: overview stats, security findings, test plan |

---

## API Services

| File | Purpose |
|------|---------|
| `api/client.ts` | Base fetch with JWT header, token storage |
| `api/auth.api.ts` | Login/register |
| `api/project.api.ts` | Project CRUD and zip upload |
| `api/analysis.api.ts` | Trigger analysis, list jobs, fetch report |

---

## Hooks

| Hook | Purpose |
|------|---------|
| `useJobSocket` | WebSocket connection; calls callback on `job_updated` events |

---

## Context

| Provider | Purpose |
|----------|---------|
| `AuthContext` | Manages auth token state and login/logout |

---

## Navigation

Simple view-state navigation in `App.tsx` (no react-router):
- Unauthenticated → LoginPage
- Authenticated → DashboardPage
- Project selected → ProjectPage

---

## Dev Setup

```powershell
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. API and WebSocket proxied to MS1:
- `/api/*` → `http://localhost:3000`
- `/ws` → `ws://localhost:3000`

---

## State Management

- Auth token: localStorage + AuthContext
- Page view: React useState in App.tsx
- Job list: React useState in ProjectPage, updated via WebSocket + REST
