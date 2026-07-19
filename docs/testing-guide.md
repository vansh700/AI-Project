# Full Repository End-to-End Testing Guide

This guide walks through testing the entire application from registration to repository parsing and graph database visualization using a real GitHub repository downloaded as a `.zip` archive.

---

## Prerequisites
1. Docker Compose services must be running (`docker compose up -d`).
2. MS1 Core API running (`npm run dev` in the `ms1` folder on port `3000`).
3. MS2 Worker Pool running (`python -m uvicorn app.main:app --port 8000 --reload` in the `ms2` folder).
4. Frontend running (`npm run dev` in the `frontend` folder on port `5173`) — required for Phase 9 UI testing.
5. A REST Client (Postman) or terminal with `curl` / `curl.exe` configured.

---

## Step 1: Obtain a Real GitHub Repository ZIP
To perform a realistic test, download the codebase of a real, lightweight public repository:
1. Open your browser and download this ZIP directly from GitHub:
   - **Target Repository**: Express.js
   - **Download Link**: [https://github.com/expressjs/express/archive/refs/heads/master.zip](https://github.com/expressjs/express/archive/refs/heads/master.zip)
2. Save it locally on your computer. 
   - *Example Path*: `C:/Users/Vansh/Downloads/express-master.zip`

---

## Step 2: User Onboarding (Authentication)

### 1. Register a New User
- **HTTP Method**: `POST`
- **URL**: `http://localhost:3000/auth/register`
- **Headers**:
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "email": "tester@example.com",
    "password": "password123"
  }
  ```
- **Postman Setup**:
  - Set method to `POST` and enter the URL.
  - Go to the **Body** tab -> Select **raw** -> Select **JSON**. Paste the payload above. Click **Send**.
- **Alternative Terminal Command**:
  ```powershell
  curl.exe -X POST http://localhost:3000/auth/register -H "Content-Type: application/json" -d '{"email":"tester@example.com","password":"password123"}'
  ```
- **Expected Response** (`201 Created`):
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbXJuZW1zOXcwMDAwNGxtMTl0ZDNrZGt2Ii..."
  }
  ```
- *Action*: Copy the `"token"` value.

### 2. User Login (If already registered)
If you already registered your user, obtain a token via the login endpoint:
- **HTTP Method**: `POST`
- **URL**: `http://localhost:3000/auth/login`
- **Headers**:
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "email": "tester@example.com",
    "password": "password123"
  }
  ```
- **Alternative Terminal Command**:
  ```powershell
  curl.exe -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" -d '{"email":"tester@example.com","password":"password123"}'
  ```
- **Expected Response** (`200 OK`): Same token payload structure as registration.

---

## Step 3: Register a Project

Create a new project record to bind your repository metadata to.
- **HTTP Method**: `POST`
- **URL**: `http://localhost:3000/projects`
- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer <YOUR_TOKEN>` (replace with the token copied in Step 2)
- **Body (JSON)**:
  ```json
  {
    "name": "Express Framework Test",
    "repoUrl": "https://github.com/expressjs/express"
  }
  ```
- **Alternative Terminal Command**:
  ```powershell
  curl.exe -X POST http://localhost:3000/projects -H "Authorization: Bearer <YOUR_TOKEN>" -H "Content-Type: application/json" -d '{"name":"Express Framework Test","repoUrl":"https://github.com/expressjs/express"}'
  ```
- **Expected Response** (`201 Created`):
  ```json
  {
    "project": {
      "id": "cmrneoj3g00024lm12jmtrskl",
      "name": "Express Framework Test",
      "repoUrl": "https://github.com/expressjs/express",
      "storagePath": null,
      "ownerId": "cmrnems...",
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```
- *Action*: Copy the `"id"` of the created project. This is your `<PROJECT_ID>`.

---

## Step 4: Upload the GitHub Repository ZIP

Upload your downloaded `express-master.zip` file to your newly registered project.
- **HTTP Method**: `POST`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/upload` (replace with project ID)
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
  - **CRITICAL**: Do **NOT** set the `Content-Type` header manually. Postman will automatically set it and configure the multipart boundaries.
- **Body (form-data)**:
  - **Key**: `file`
  - **Key Type**: Hover over the key input box, change the dropdown from **Text** to **File**.
  - **Value**: Click **Select Files** and choose `express-master.zip` from your downloads.
- **Alternative Terminal Command** (Replace path to file):
  ```powershell
  curl.exe -X POST http://localhost:3000/projects/<PROJECT_ID>/upload -H "Authorization: Bearer <YOUR_TOKEN>" -F "file=@C:/Users/Vansh/Downloads/express-master.zip"
  ```
- **Expected Response** (`200 OK`):
  ```json
  {
    "project": {
      "id": "<PROJECT_ID>",
      "name": "Express Framework Test",
      "repoUrl": "https://github.com/expressjs/express",
      "storagePath": "C:\\Users\\Vansh\\Downloads\\AI-project\\ms1\\storage\\uploads\\<OWNER_ID>\\<PROJECT_ID>\\express-master.zip",
      "ownerId": "<OWNER_ID>",
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```

---

## Step 5: Trigger Repository Analysis

Queue the asynchronous intelligence parsing job.
- **HTTP Method**: `POST`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/analysis`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
- **Alternative Terminal Command**:
  ```powershell
  curl.exe -X POST http://localhost:3000/projects/<PROJECT_ID>/analysis -H "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Expected Response** (`202 Accepted`):
  ```json
  {
    "job": {
      "id": "cmrxxxxxxxxxxxxx",
      "status": "QUEUED",
      "projectId": "<PROJECT_ID>",
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```
- *Action*: Copy the `"id"` of the job. This is your `<JOB_ID>`.

---

## Step 6: Monitor Processing in Logs

### 1. MS2 Worker Console
Observe the FastAPI terminal. You should see logs mapping the ingestion pipeline:
```
INFO: Job received | bullJobId=1 dbJobId=cmrnim2h... projectId=...
INFO: Extracting zip | src=C:\...\express-master.zip dest=C:\Users\Vansh\AppData\Local\Temp\ms2_repo_...
INFO: Walking repository tree | root=C:\Users\Vansh\AppData\Local\Temp\ms2_repo_...
INFO: Walk complete | dirs=12 files=84
INFO: Building graph | jobId=cmrnim2h... projectId=...
INFO: Graph built successfully | jobId=cmrnim2h... dirs=12 files=84
INFO: Detected environment | lang=JavaScript framework=Express. Running AI planner...
INFO: run_planner | starting | job_id=cmrnim2h...
INFO: run_planner | completed | job_id=cmrnim2h... testCases=8
INFO: run_execution | starting | job_id=cmrnim2h... cases=8 lang=JavaScript
INFO: Launching sandbox | image=node:20-alpine cases=8 repo=...
INFO: run_execution | completed | job_id=cmrnim2h... passed=6 failed=2
INFO: run_security_scan | starting | job_id=cmrnim2h... files=84
INFO: run_security_scan | completed | job_id=cmrnim2h... findings=5 critical=1
INFO: Webhook delivered | jobId=cmrnim2h... status=COMPLETED
INFO: Job completed | dbJobId=cmrnim2h... dirs=12 files=84 with_plan=True with_execution=True with_security=True
INFO: Temp directory cleaned up | path=C:\Users\Vansh\AppData\Local\Temp\ms2_repo_...
```

### 2. MS1 API Console
Observe the Express terminal. Verify it receives the webhook completed message:
```
info: Job status updated via webhook {"jobId":"cmrnim2h...","status":"COMPLETED"}
```

---

## Step 7: Verify Results

### 1. Check PostgreSQL Database Status
Verify that the status of the job in PostgreSQL has successfully updated:
- **HTTP Method**: `GET`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/analysis`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
- **Alternative Terminal Command**:
  ```powershell
  curl.exe -X GET http://localhost:3000/projects/<PROJECT_ID>/analysis -H "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Expected Response** (`200 OK`):
  ```json
  {
    "jobs": [
      {
        "id": "<JOB_ID>",
        "status": "COMPLETED",
        "projectId": "<PROJECT_ID>",
        "createdAt": "...",
        "updatedAt": "..."
      }
    ]
  }
  ```

### 2. Visualize Knowledge Graph in Neo4j
1. Open your browser and go to: `http://localhost:7474`
2. Connect with credentials:
   - **Username**: `neo4j`
   - **Password**: `neo4j_password`
3. In the query box at the top, run:
    ```cypher
    MATCH (n) RETURN n LIMIT 100
   ```
4. You should see a beautiful visual map where the green `Repository` node is linked to blue `Directory` nodes (e.g. `lib`, `test`, `benchmarks`) and orange `File` nodes (e.g. `package.json`, `index.js`, `Readme.md`), confirming that the codebase has been completely mapped!

---

## Step 8: Verify AI Test Plan (Phase 6)

After the job completes, the worker runs the LangGraph AI planner and stores the result in both MS2 PostgreSQL and MS1's `planSummary` field.

### 1. Check MS2 Worker Logs
Look for planner-related log lines after the graph build step:
```
INFO: Detected environment | lang=JavaScript framework=Express. Running AI planner...
INFO: run_planner | starting | job_id=<JOB_ID> project_id=<PROJECT_ID>
INFO: intake_node | analysisId=<JOB_ID> path=...
INFO: context_node | fetching Neo4j subgraph
INFO: context_node | nodes=<N>
INFO: plan_node | checking environment and API keys
INFO: plan_node | plan generated | testCases=<N>
INFO: reflect_node | validated testCases=<N>
INFO: save_plan | persisted | job_id=<JOB_ID>
INFO: run_planner | completed | job_id=<JOB_ID> testCases=<N>
INFO: Job completed | dbJobId=<JOB_ID> dirs=<N> files=<N> with_plan=True
```

> **Note**: If `OPENAI_API_KEY` is not set in `ms2/.env`, the planner uses a mock test plan automatically. Set a valid key to test real LLM generation.

### 2. Verify planSummary in MS1 Response
Re-fetch the analysis jobs list and confirm the `planSummary` field is populated:
- **HTTP Method**: `GET`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/analysis`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
- **Expected Response** (`200 OK`):
  ```json
  {
    "jobs": [
      {
        "id": "<JOB_ID>",
        "status": "COMPLETED",
        "projectId": "<PROJECT_ID>",
        "planSummary": {
          "summary": "Test plan for ...",
          "language": "JavaScript",
          "framework": "Express",
          "testCases": [
            {
              "id": "TC-001",
              "target": "lib/application.js",
              "description": "...",
              "type": "unit",
              "priority": "high"
            }
          ],
          "coverage": {
            "endpoints": 0,
            "services": 2,
            "models": 0
          }
        },
        "createdAt": "...",
        "updatedAt": "..."
      }
    ]
  }
  ```

### 3. Verify Planner State in MS2 PostgreSQL
Connect to the MS2 database (port `5433`) and query the planner state:
```sql
SELECT job_id, status, plan->'testCases' AS test_cases
FROM planner_states
WHERE job_id = '<JOB_ID>';
```
Expected: one row with `status = 'COMPLETED'` and a JSON plan payload.

---

## Step 9: Verify Docker Sandbox Execution (Phase 7)

After the AI planner generates test cases, the worker launches a locked-down Docker container to validate each target file.

### Prerequisites
- **Docker Desktop** must be running on your machine.
- Set `DOCKER_ENABLED=true` in `ms2/.env` (default).

### 1. Check MS2 Worker Logs
Look for execution-related log lines after the planner step:
```
INFO: run_execution | starting | job_id=<JOB_ID> cases=8 lang=JavaScript
INFO: Launching sandbox | image=node:20-alpine cases=8 repo=...
INFO: save_execution | persisted | job_id=<JOB_ID>
INFO: run_execution | completed | job_id=<JOB_ID> passed=6 failed=2
INFO: Job completed | dbJobId=<JOB_ID> dirs=<N> files=<N> with_plan=True with_execution=True
```

> **Note**: If Docker is not running, execution falls back to mock/skipped results with `sandbox: "mock"`.

### 2. Verify executionSummary in MS1 Response
Re-fetch the analysis jobs list and confirm the `executionSummary` field is populated:
- **HTTP Method**: `GET`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/analysis`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
- **Expected Response** (`200 OK`):
  ```json
  {
    "jobs": [
      {
        "id": "<JOB_ID>",
        "status": "COMPLETED",
        "projectId": "<PROJECT_ID>",
        "planSummary": { "..." : "..." },
        "executionSummary": {
          "summary": "Executed 8 tests in JavaScript sandbox",
          "language": "JavaScript",
          "framework": "Express",
          "totalTests": 8,
          "passed": 6,
          "failed": 2,
          "skipped": 0,
          "durationMs": 4500,
          "sandbox": "docker",
          "results": [
            {
              "testCaseId": "TC-001",
              "target": "lib/application.js",
              "status": "passed",
              "message": "Syntax check passed",
              "durationMs": 0
            }
          ]
        }
      }
    ]
  }
  ```

### 3. Verify Execution Log in MS2 PostgreSQL
Connect to the MS2 database (port `5433`) and query:
```sql
SELECT job_id, status, summary->'passed' AS passed, summary->'failed' AS failed
FROM execution_logs
WHERE job_id = '<JOB_ID>';
```
Expected: one row with `status = 'COMPLETED'` and a JSON summary payload.

---

## Step 10: Verify Dynamic Security Scan (Phase 8)

After Docker execution, the worker runs three security scan types: pattern rules, sensitive file detection, and auth coverage probes.

### 1. Check MS2 Worker Logs
Look for security-related log lines after the execution step:
```
INFO: run_security_scan | starting | job_id=<JOB_ID> files=84
INFO: pattern_scanner | completed | findings=3
INFO: sensitive_file_scanner | completed | findings=0
INFO: auth_probe | completed | findings=2
INFO: save_security_scan | persisted | job_id=<JOB_ID>
INFO: run_security_scan | completed | job_id=<JOB_ID> findings=5 critical=1
INFO: Job completed | ... with_security=True
```

### 2. Verify securitySummary in MS1 Response
Re-fetch the analysis jobs list and confirm the `securitySummary` field is populated:
- **HTTP Method**: `GET`
- **URL**: `http://localhost:3000/projects/<PROJECT_ID>/analysis`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_TOKEN>`
- **Expected Response** (`200 OK`):
  ```json
  {
    "jobs": [
      {
        "id": "<JOB_ID>",
        "status": "COMPLETED",
        "securitySummary": {
          "summary": "Found 1 critical, 2 high, 2 medium findings",
          "language": "JavaScript",
          "framework": "Express",
          "totalFindings": 5,
          "critical": 1,
          "high": 2,
          "medium": 2,
          "low": 0,
          "durationMs": 450,
          "findings": [
            {
              "id": "SEC-001",
              "ruleId": "hardcoded-secret",
              "severity": "critical",
              "title": "Hardcoded secret or API key",
              "file": "src/config.js",
              "line": 12,
              "evidence": "api_key = 'sk-...'",
              "recommendation": "Move secrets to environment variables or a secrets manager.",
              "type": "pattern"
            }
          ]
        }
      }
    ]
  }
  ```

### 3. Verify Security Log in MS2 PostgreSQL
Connect to the MS2 database (port `5433`) and query:
```sql
SELECT job_id, status, summary->'totalFindings' AS total, summary->'critical' AS critical
FROM security_logs
WHERE job_id = '<JOB_ID>';
```
Expected: one row with `status = 'COMPLETED'` and a JSON summary payload.

---

## Step 11: Verify Frontend & Reports (Phase 9)

### Prerequisites
Add a fourth terminal for the frontend:
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`

Also apply the MS1 migration if not done:
```powershell
cd ms1
npx prisma migrate deploy
npx prisma generate
```

### 1. Login / Register
Use the UI to register or login. You should land on the **Projects** dashboard.

### 2. Create Project & Upload
- Click **New Project**, enter name and repo URL
- Open the project → **Upload ZIP** → select your test zip
- Click **Run Analysis**

### 3. Watch Real-Time Status
Job status should update live via WebSocket:
- `QUEUED` → immediately after trigger
- `RUNNING` → when MS2 picks up the job
- `COMPLETED` → when pipeline finishes

No page refresh needed.

### 4. View Report
When status is `COMPLETED`, click **View Report**. You should see:
- Overview stats (language, framework, test counts, security findings)
- Security findings table (if any)
- Test plan JSON section

### 5. Verify Report API
```powershell
curl.exe -X GET "http://localhost:3000/projects/<PROJECT_ID>/analysis/<JOB_ID>/report" -H "Authorization: Bearer <TOKEN>"
```
Expected: `200 OK` with `{ "report": { "overview": {...}, "plan": {...}, ... } }`

### 6. Verify reportSummary in DB
```sql
SELECT id, status, "reportSummary"->'overview' AS overview
FROM "AnalysisJob"
WHERE id = '<JOB_ID>';
```
Expected: `reportSummary` populated with overview stats.
