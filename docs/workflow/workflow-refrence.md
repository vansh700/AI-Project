# Workflow Reference

## Repository Analysis (End-to-End)

### Step 1 — User triggers analysis
Frontend (or REST client) sends `POST /projects/:id/analysis` to MS1.

### Step 2 — MS1 enqueues job
MS1 validates ownership, creates `AnalysisJob` (status: `QUEUED`), pushes to BullMQ `analysis-queue`, returns `202` with job ID.

### Step 3 — MS2 worker picks up job
MS2 BullMQ worker fetches job payload `{ jobId, projectId, storagePath }`.

### Step 4 — Repository intelligence (Phase 5)
- Extract uploaded zip to temp directory
- Walk file tree with language detection
- Build Neo4j knowledge graph

### Step 5 — AI planning (Phase 6)
- LangGraph pipeline: intake → context → plan → reflect
- Persist plan to MS2 `planner_states`
- Plan includes `testCases[]`

### Step 6 — Docker execution (Phase 7)
- Launch locked-down sandbox container
- Validate each test-case target (syntax + file checks)
- Persist results to MS2 `execution_logs`

### Step 7 — Security scan (Phase 8)
- Pattern scanner (secrets, SQLi, eval, CORS, JWT)
- Sensitive file scanner (.env, keys, credentials)
- Auth coverage probe (routes without auth)
- Persist findings to MS2 `security_logs`

### Step 8 — Webhook callback
MS2 sends `POST /webhooks/job-complete` to MS1 with:
- `status: "COMPLETED"`
- `planSummary`, `executionSummary`, `securitySummary`

### Step 9 — MS1 updates job
MS1 persists all summary fields on `AnalysisJob`, returns `200`.

### Step 10 — Frontend reads results
`GET /projects/:id/analysis` returns job with all summary fields.
Frontend connects to `WS /ws?token=<JWT>` for live updates.

### Step 11 — Report API (Phase 9)
`GET /projects/:id/analysis/:jobId/report` returns unified `reportSummary`.

---

## Job Status Transitions

```
QUEUED → RUNNING → COMPLETED
                 ↘ FAILED
```

---

## Data Ownership

| Data | Owner | Storage |
|------|-------|---------|
| Users, Projects, Jobs | MS1 | PostgreSQL (MS1) |
| Planner state | MS2 | PostgreSQL (MS2) — `planner_states` |
| Execution logs | MS2 | PostgreSQL (MS2) — `execution_logs` |
| Security findings | MS2 | PostgreSQL (MS2) — `security_logs` |
| Knowledge graph | MS2 | Neo4j |

MS1 receives summary copies via webhook only — never reads MS2 DB directly.
