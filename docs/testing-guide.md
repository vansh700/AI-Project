# Full Repository End-to-End Testing Guide

This guide walks through testing the entire application from registration to repository parsing and graph database visualization using a real GitHub repository downloaded as a `.zip` archive.

---

## Prerequisites
1. Docker Compose services must be running (`docker compose up -d`).
2. MS1 Core API running (`npm run dev` in the `ms1` folder on port `3000`).
3. MS2 Worker Pool running (`uvicorn app.main:app --port 8000 --reload` in the `ms2` folder on port `8000`).
4. A REST Client (Postman) or terminal with `curl` / `curl.exe` configured.

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
INFO: Webhook delivered | jobId=cmrnim2h... status=COMPLETED
INFO: Job completed | dbJobId=cmrnim2h... dirs=12 files=84
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
