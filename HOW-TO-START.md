# HOW TO START: Agno Agent API & UI Development Environment

## Prerequisites
- Docker Desktop installed and running (for backend)
- Node.js and npm installed (for UI)
- Python 3.12+ (for development, handled by setup script)
- API keys set in `.env` (e.g., ANTHROPIC_API_KEY, OPENAI_API_KEY)

---

## 1. Setup Backend (agent-api)

### a. Clone the repository
```
git clone https://github.com/agno-agi/agent-api.git
cd agent-api
```

### b. Install Python dependencies (for development)
```
./scripts/dev_setup.sh
source .venv/bin/activate
```

### c. Configure environment variables
- Copy `.env.example` to `.env` and add your API keys (e.g., ANTHROPIC_API_KEY, OPENAI_API_KEY).

### d. Start the backend server (FastAPI + Postgres)
```
docker compose -f compose.yaml up -d
```
- This starts the FastAPI server and Postgres database.
- Default API endpoint: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## 2. Setup Frontend (agent-ui)

### a. Clone the repository
```
git clone https://github.com/agno-agi/agent-ui.git
cd agent-ui
```

### b. Install dependencies
```
npm install
```

### c. Start the development server
```
npm run dev
```
- Default UI: http://localhost:3000

---

## 3. Stopping the Environment

### a. Stop backend
```
docker compose -f compose.yaml down
```

### b. Stop frontend
- Press Ctrl+C in the terminal running `npm run dev`.

---

## 4. Troubleshooting
- If you see `ModuleNotFoundError` or backend won't start, always use Docker Compose as above.
- Ensure `.env` is correctly set for both backend and frontend.
- For more info, see README.md in each repo.

---

## 5. Quick Reference
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend UI: http://localhost:3000

---

**Always use Docker Compose for backend startup unless you are actively developing the API internals.**
