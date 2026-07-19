Frontend

↓

analysis.api.ts

↓

POST /analysis

↓

analysis.routes.ts

↓

analysis.controller.ts

↓

analysis.service.ts

↓

analysis.repository.ts

↓

Prisma

↓

PostgreSQL

↓

BullMQ

↓

MS2 Worker
  ├── extract zip
  ├── walk tree
  ├── build Neo4j graph
  ├── run_planner (LangGraph)
  ├── run_execution (Docker sandbox)
  ├── run_security_scan (pattern + sensitive file + auth probe)
  └── webhook → MS1
        ├── planSummary
        ├── executionSummary
        ├── securitySummary
        └── reportSummary (built on COMPLETED)
  └── WebSocket job_updated → Frontend