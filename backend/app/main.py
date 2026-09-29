from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents.orchestrator import SocOrchestrator
from .config import settings
from .demo import brute_force, container_attack, normal_traffic, port_scan

app = FastAPI(title="Autonomous Cloud SOC API", version="0.1.0", description="Demo-mode autonomous SOC pipeline")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
orchestrator = SocOrchestrator()


@app.get("/api/health")
def health():
    return {"status": "healthy", "response_mode": settings.response_mode, "storage": "local-json"}


@app.get("/api/events")
def events():
    return sorted(orchestrator.store.all("events"), key=lambda item: item["timestamp"], reverse=True)[:250]


@app.get("/api/events/{event_id}")
def event(event_id: str):
    result = orchestrator.store.get("events", event_id)
    if not result:
        raise HTTPException(404, "Event not found")
    return result


@app.get("/api/incidents")
def incidents():
    return orchestrator.incidents()


@app.get("/api/incidents/{incident_id}")
def incident(incident_id: str):
    result = orchestrator.store.get("incidents", incident_id)
    if not result:
        raise HTTPException(404, "Incident not found")
    return result


@app.post("/api/incidents/{incident_id}/respond")
def respond(incident_id: str):
    result = orchestrator.store.get("incidents", incident_id)
    if not result:
        raise HTTPException(404, "Incident not found")
    return {"incident_id": incident_id, "response": result.get("response"), "note": "Responses are allowlisted and simulated by default."}


@app.get("/api/reports/{incident_id}")
def report(incident_id: str):
    result = next((item for item in orchestrator.store.all("reports") if item["incident_id"] == incident_id), None)
    if not result:
        raise HTTPException(404, "Report not found")
    return result


@app.get("/api/agents/status")
def agents():
    return orchestrator.agent_status()


@app.get("/api/agents/{agent_name}/runs")
def agent_runs(agent_name: str):
    return [run for run in orchestrator.store.all("agent_runs") if run["agent"].lower() == agent_name.lower()][-100:]


@app.get("/api/ai/status")
def ai_status():
    return orchestrator.ai.status()


@app.get("/api/metrics")
def metrics():
    return orchestrator.metrics()


@app.post("/api/demo/bruteforce")
def demo_bruteforce():
    return brute_force(orchestrator)


@app.post("/api/demo/port-scan")
def demo_port_scan():
    return port_scan(orchestrator)


@app.post("/api/demo/container-attack")
def demo_container_attack():
    return container_attack(orchestrator)


@app.post("/api/demo/normal-traffic")
def demo_normal_traffic():
    return {"events": [event.model_dump(mode="json") for event in normal_traffic(orchestrator)]}


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics():
    metrics = orchestrator.metrics()
    return "\n".join(f"soc_{key} {value}" for key, value in metrics.items() if isinstance(value, (int, float))) + "\n"
