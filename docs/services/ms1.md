# MS1 — Core API

MS1 is the Express.js API that handles authentication, project management, job lifecycle, and webhook callbacks from MS2.

---

## Webhook

**Module**: `ms1/src/modules/webhook/webhook.controller.ts`

**Endpoint**: `POST /webhooks/job-complete`

**Purpose**: Receives job completion callbacks from MS2 and updates `AnalysisJob` status and summary fields.

**Authentication**: `X-Webhook-Secret` header (shared secret with MS2).

**Request body**:
```json
{
  "jobId": "string",
  "status": "COMPLETED | FAILED | RUNNING",
  "error": "optional string",
  "planSummary": "optional JSON — AI test plan (Phase 6)",
  "executionSummary": "optional JSON — Docker execution results (Phase 7)",
  "securitySummary": "optional JSON — security scan findings (Phase 8)"
}
```

**Response**: `200 OK` with updated `job` object.

**Persists to**: `AnalysisJob` table — `status`, `planSummary`, `executionSummary`, `securitySummary`.

---

## Analysis

**Module**: `analysis.controller.ts`, `analysis.service.ts`, `analysis.repository.ts`

**Endpoints**:
- `POST /projects/:id/analysis` — trigger analysis job
- `GET /projects/:id/analysis` — list jobs for project

**GET response fields** (per job):
- `id`, `status`, `projectId`, `createdAt`, `updatedAt`
- `planSummary` — AI-generated test plan (Phase 6)
- `executionSummary` — Docker sandbox results (Phase 7)
- `securitySummary` — security scan findings (Phase 8)
- `reportSummary` — unified report compiled on completion (Phase 9)

**Additional endpoints** (Phase 9):
- `GET /projects/:id/analysis/:jobId` — single job
- `GET /projects/:id/analysis/:jobId/report` — unified report

---

## WebSocket

**Path**: `/ws?token=<JWT>`

**Purpose**: Real-time job status updates to authenticated frontend clients.

**Events emitted**:
- `connected` — on successful connection
- `job_updated` — when job is created or webhook updates status

**Payload** (`job_updated`):
```json
{ "event": "job_updated", "job": { /* AnalysisJob */ } }
```

**Triggered by**:
- `analysis.service.ts` — when analysis is triggered (QUEUED)
- `webhook.controller.ts` — when MS2 sends RUNNING/COMPLETED/FAILED

---

## Report

**Module**: `ms1/src/modules/report/report.service.ts`

**Purpose**: Compiles `reportSummary` from `planSummary`, `executionSummary`, and `securitySummary`.

**Built on**: Webhook COMPLETED (persisted to DB) or on-demand via GET report endpoint.

---

---

## Auth

**Endpoints**: `POST /auth/register`, `POST /auth/login`

**Returns**: JWT token used for all protected routes.

---

## Projects

**Endpoints**: `POST /projects`, `GET /projects`, `GET /projects/:id`, `POST /projects/:id/upload`

**Ownership**: Users can only access their own projects.
