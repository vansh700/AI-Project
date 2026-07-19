# API Reference

## MS1 — Public APIs

### POST /auth/register

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | None |
| Body | `{ "email": string, "password": string }` |
| Response | `201` — `{ "token": string }` |

### POST /auth/login

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | None |
| Body | `{ "email": string, "password": string }` |
| Response | `200` — `{ "token": string }` |

### POST /projects

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Body | `{ "name": string, "repoUrl": string }` |
| Response | `201` — `{ "project": Project }` |

### GET /projects

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `200` — `{ "projects": Project[] }` |

### GET /projects/:id

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `200` — `{ "project": Project }` |

### POST /projects/:id/upload

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Body | `multipart/form-data` — `file` (.zip) |
| Response | `200` — `{ "project": Project }` |

### POST /projects/:id/analysis

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `202` — `{ "job": AnalysisJob }` |

### GET /projects/:id/analysis

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `200` — `{ "jobs": AnalysisJob[] }` |

**AnalysisJob fields**:
```json
{
  "id": "string",
  "status": "QUEUED | RUNNING | COMPLETED | FAILED",
  "projectId": "string",
  "planSummary": "JSON | null",
  "executionSummary": "JSON | null",
  "securitySummary": "JSON | null",
  "reportSummary": "JSON | null",
  "createdAt": "ISO8601",
  "updatedAt": "ISO8601"
}
```

---

## MS1 — Internal APIs

### POST /webhooks/job-complete

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | `X-Webhook-Secret` header |
| Caller | MS2 only |
| Body | `{ "jobId", "status", "error?", "planSummary?", "executionSummary?", "securitySummary?" }` |
| Response | `200` — `{ "job": AnalysisJob }` |

### GET /projects/:id/analysis/:jobId

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `200` — `{ "job": AnalysisJob }` |

### GET /projects/:id/analysis/:jobId/report

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | Bearer JWT |
| Response | `200` — `{ "report": ReportSummary }` |

**ReportSummary fields**: `generatedAt`, `jobId`, `projectId`, `status`, `overview`, `plan`, `execution`, `security`

---

## MS1 — WebSocket

### WS /ws?token=\<JWT\>

| Field | Value |
|-------|-------|
| Owner | MS1 |
| Auth | JWT in query param |
| Events | `connected`, `job_updated` |
| Payload | `{ "event": "job_updated", "job": AnalysisJob }` |

---

MS2 has no public business APIs. Only `GET /health` is exposed.

Worker pipeline produces data sent to MS1 via webhook:
- `planSummary` — Phase 6
- `executionSummary` — Phase 7
- `securitySummary` — Phase 8
