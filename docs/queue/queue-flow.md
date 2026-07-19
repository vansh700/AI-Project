# Queue Flow

## Analysis Queue

| Property | Value |
|----------|-------|
| Queue name | `analysis-queue` |
| Producer | MS1 (`analysis.service.ts` → BullMQ) |
| Consumer | MS2 Worker (`ms2/app/queue/worker.py`) |
| Retry | 3 attempts, exponential backoff (5s base) |
| Dead Letter | BullMQ default (failed after retries) |

### Job Payload

```json
{
  "jobId": "AnalysisJob.id",
  "projectId": "Project.id",
  "storagePath": "/path/to/uploaded.zip",
  "userId": "User.id"
}
```

### MS2 Worker Pipeline (Phase 9)

```
1. POST RUNNING webhook to MS1
2. Extract zip archive
3. Walk repository file tree
4. Build Neo4j knowledge graph
5. Run AI planner (LangGraph)
6. Execute test plan in Docker sandbox
7. Run dynamic security scan
8. POST COMPLETED webhook to MS1 (planSummary + executionSummary + securitySummary)
9. MS1 builds reportSummary and emits WebSocket job_updated
10. Clean up temp directory
```

### Job Lifecycle (MS1)

```
QUEUED → (worker picks up) → RUNNING → COMPLETED
                                      ↘ FAILED
```

### Webhook Callback

MS2 sends `POST /webhooks/job-complete` to MS1 with:
- `jobId`, `status` (RUNNING at start, COMPLETED at end)
- `planSummary`, `executionSummary`, `securitySummary`

MS1 updates `AnalysisJob`, builds `reportSummary` on COMPLETED, emits WebSocket `job_updated`.

### Failure Handling

- Planner failure: logged, job continues without `planSummary`
- Execution failure: logged, job continues without `executionSummary`
- Security scan failure: logged, job continues without `securitySummary`
- Pipeline failure (extract/graph): job marked `FAILED`, webhook sent with error
