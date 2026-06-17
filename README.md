# Infra Swarm - Infrastructure Agent Swarm

A from-scratch MVP for a production-style AI SRE agent swarm.

This version runs locally on your MacBook and includes:

- FastAPI backend
- Six-agent incident workflow
- React dashboard
- Incident simulator
- Safety gates and approval flow
- RAG-style runbook matching using local keyword retrieval
- Optional OpenAI-compatible LLM integration later

## Architecture

```text
React Dashboard
      ↓
FastAPI Backend
      ↓
Agent Swarm
      ↓
Simulated Metrics / Logs / Incidents
```

## Agents

- Observer: detects anomalies
- Diagnoser: finds likely root cause
- Remediator: selects a runbook and proposes action
- Safety: approves, blocks, or requires human approval
- Orchestrator: controls incident state machine
- Learner: stores outcomes and recommends similar runbooks

## Run on MacBook

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### 2. Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

### 3. Test an incident

In the dashboard, click:

```text
Inject Memory Leak
```

Or use terminal:

```bash
curl -X POST http://localhost:8000/simulate/memory-leak
```

## Current MVP Behavior

1. Simulator injects a memory leak incident.
2. Observer detects anomaly.
3. Orchestrator creates incident.
4. Diagnoser analyzes metrics/logs/deployment evidence.
5. Remediator maps diagnosis to a runbook.
6. Safety checks policy.
7. If approval is required, dashboard shows approval button.
8. Remediator executes safe simulated action.
9. Observer validates recovery.
10. Learner stores outcome.

## Suggested next steps

- Replace simulator with Docker Compose microservices.
- Add Prometheus metrics ingestion.
- Add Loki log ingestion.
- Add OpenTelemetry traces.
- Add pgvector or Chroma for real RAG.
- Add Kubernetes remediation commands.
- Add Slack approval workflow.
# Infra-Swarm
