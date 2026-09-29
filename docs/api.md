# API

FastAPI publishes interactive OpenAPI documentation at `http://localhost:8000/docs`.

| Route | Purpose |
| --- | --- |
| `GET /api/health` | Backend health and active mode |
| `GET /api/events` | Recent normalized event records |
| `GET /api/incidents` | Incident records |
| `GET /api/incidents/{id}` | Full incident timeline and evidence |
| `GET /api/agents/status` | Agent status and execution metrics |
| `GET /api/agents/{agent_name}/runs` | Recent redacted execution records for one agent |
| `GET /api/ai/status` | Redacted Gemini provider and key-pool health |
| `POST /api/demo/*` | Runs a controlled demo generator |
| `GET /api/reports/{id}` | Structured report |
| `GET /api/metrics`, `GET /metrics` | Dashboard and Prometheus-compatible metrics |
