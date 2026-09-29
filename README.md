# SentinelFlow

A working, demo-mode prototype for an agentic cloud security operations center. It ingests normalized security events, applies transparent rule-based detection, hunts related history, calculates explainable risk, performs an allowlisted simulated response, produces an incident report, and exposes the complete pipeline in a React dashboard.

## Stack

- Frontend: React, Vite, Tailwind-ready CSS, Lucide icons
- Backend: Python, FastAPI, Pydantic, Uvicorn
- Storage: local JSON persistence by default; Firestore is an intended replaceable data layer
- AI reasoning: optional backend-only Gemini service with structured output and deterministic fallback
- Deployment: Docker Compose and Minikube-ready manifests

## Quick start

Copy `.env.example` to `.env` if you need to change settings. The default `RESPONSE_MODE=simulation` must remain in use for the demo.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API documentation is at `http://localhost:8000/docs`.

## Docker

```powershell
docker compose up --build
```

The dashboard is served at `http://localhost:8080`; the API is at `http://localhost:8000`.

For Gemini, set `GEMINI_MODEL` and either numbered `GEMINI_API_KEY_*` environment variables or `GEMINI_KEY_FILE` in the local ignored `.env`. Do not place credential values in `docker-compose.yml` or Kubernetes manifests.

## Tests

```powershell
cd backend
pytest
```

Tests cover event normalization, brute-force detection, port-scan detection, container response selection, incident report creation, and API health. The brute-force test exercises the complete pipeline.

## Deployment

For Minikube, build images inside the cluster Docker environment, then apply the manifests:

```powershell
minikube start
minikube image build -t autonomous-soc-backend:latest ./backend
minikube image build -t autonomous-soc-frontend:latest ./frontend
kubectl apply -f k8s
kubectl port-forward service/soc-frontend 8080:80
```

Run `kubectl port-forward service/soc-backend 8000:8000` in another terminal if API access is needed from the host. The current Kubernetes storage is ephemeral `emptyDir`, deliberately suitable only for a demo.

## Security notes and roadmap

No credentials are committed. The response agent never runs arbitrary commands and supports only allowlisted actions. Simulation is the default and is visibly labeled in the dashboard. Future work: configure a Firestore implementation, implement authenticated external source ingestion, connect real policy-controlled network/Kubernetes actions, add genuine trained ML when labeled data is available, and calculate SHAP values only for an actual model.

See [architecture](docs/architecture.md), [demo](docs/demo.md), and [API reference](docs/api.md).

Gemini setup and security boundaries are documented in [Gemini integration](docs/gemini-integration.md) and [security](docs/security.md). Multiple credentials are used for health-aware request distribution and fault isolation only; they do not bypass provider quotas.
