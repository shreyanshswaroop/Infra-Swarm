# Infra Swarm - Infrastructure Agent Swarm

A from-scratch MVP for a production-style AI SRE agent swarm.

Infra Swarm runs locally and demonstrates an incident workflow across a React
dashboard, a FastAPI backend, simulated services, and a Docker Compose
`payment-service`.

## What It Includes

- FastAPI backend
- React dashboard
- Six-agent incident workflow
- Simulated service metrics, logs, and incidents
- Docker Compose `payment-service` with live health, metrics, logs, and recovery endpoints
- Safety gates and human approval flow
- RAG-style runbook matching using local keyword retrieval
- Optional OpenAI-compatible LLM integration later

## Architecture

```text
React Dashboard
      |
      v
FastAPI Backend
      |
      v
Agent Swarm
      |
      +--> Built-in simulator
      |
      +--> Docker payment-service
```

## Agents

- Observer: detects anomalies from metrics and logs
- Diagnoser: finds likely root cause
- Remediator: selects a runbook and proposes an action
- Safety: approves, blocks, or requires human approval
- Orchestrator: controls incident state transitions
- Learner: stores outcomes and recommends similar runbooks

## Prerequisites

- Python 3.12+
- Node.js and npm
- Docker Desktop, if you want to run the Docker payment service

Make sure Docker Desktop is running before using Docker Compose:

```bash
docker info
```

## Run Locally

Start each part in its own terminal.

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### 2. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

You can also use the helper script from the project root:

```bash
./start-frontend.sh
```

### 3. Start the Docker payment service

From the project root:

```bash
docker compose up --build
```

Payment service:

```text
http://localhost:9001
```

Useful payment-service endpoints:

```text
GET  http://localhost:9001/health
GET  http://localhost:9001/metrics
GET  http://localhost:9001/logs
POST http://localhost:9001/simulate/memory-leak
POST http://localhost:9001/simulate/cpu-spike
POST http://localhost:9001/recover
```

## Test Incidents

### Simulated backend incident

Use the dashboard button:

```text
Inject Memory Leak
```

Or use curl:

```bash
curl -X POST http://localhost:8000/simulate/memory-leak
```

### Docker payment-service memory leak

Start the Docker memory leak through the backend:

```bash
curl -X POST http://localhost:8000/docker/payment-service/memory-leak
```

Then ask the Observer to scan metrics:

```bash
curl -X POST http://localhost:8000/observer/scan
```

The backend should create a `payment-service` memory incident that requires
human approval. Approve it from the dashboard, or call:

```bash
curl -X POST http://localhost:8000/incidents/<incident_id>/approve
```

Approval triggers Docker recovery for `payment-service`.

## Backend API Shortcuts

```text
GET  /incidents
GET  /incidents/{incident_id}
POST /incidents/{incident_id}/approve
GET  /metrics
GET  /logs
POST /observer/scan
GET  /learned-outcomes
```

## Current MVP Behavior

1. A simulated or Docker-backed incident is injected.
2. Observer detects anomalous metrics or logs.
3. Orchestrator creates or updates incident state.
4. Diagnoser analyzes metrics, logs, and service evidence.
5. Remediator maps diagnosis to a runbook-style action.
6. Safety checks risk and decides whether human approval is required.
7. Dashboard shows approval when required.
8. Remediator executes the safe simulated or Docker recovery action.
9. Observer validates recovery.
10. Learner stores the remediation outcome.

## Troubleshooting

If the frontend page at `http://localhost:5173` does not load, start the
frontend with `npm run dev`.

If `docker compose up --build` cannot connect to Docker, start Docker Desktop
and verify it with `docker info`.

If the backend shows `payment-service` as `DOWN`, make sure Docker Compose is
running and `http://localhost:9001/health` responds.

## Suggested Next Steps

- Add Prometheus metrics ingestion
- Add Loki log ingestion
- Add OpenTelemetry traces
- Add pgvector or Chroma for real RAG
- Add Kubernetes remediation commands
- Add Slack approval workflow
