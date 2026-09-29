from pathlib import Path

from fastapi.testclient import TestClient

from app.agents.orchestrator import SocOrchestrator
from app.demo import brute_force, container_attack, port_scan
from app.main import app
from app.models import SecurityEvent
from app.models import ResponseAction
from pydantic import ValidationError
from app.store import LocalStore
from app.services.gemini_key_manager import GeminiKeyManager


def test_bruteforce_creates_high_risk_blocked_incident(tmp_path: Path):
    orchestrator = SocOrchestrator(LocalStore(tmp_path))
    incident = brute_force(orchestrator)
    assert incident is not None
    assert incident.threat_type == "BRUTE_FORCE"
    assert incident.risk.level == "HIGH"
    assert incident.response.action == "BLOCK_IP"
    assert incident.report["incident_id"] == incident.id


def test_port_scan_detection(tmp_path: Path):
    incident = port_scan(SocOrchestrator(LocalStore(tmp_path)))
    assert incident.threat_type == "PORT_SCAN"
    assert incident.response.action == "BLOCK_IP"


def test_container_attack_is_quarantined(tmp_path: Path):
    incident = container_attack(SocOrchestrator(LocalStore(tmp_path)))
    assert incident.risk.level == "CRITICAL"
    assert incident.response.action == "QUARANTINE_CONTAINER"


def test_event_normalization(tmp_path: Path):
    orchestrator = SocOrchestrator(LocalStore(tmp_path))
    orchestrator.process_event(SecurityEvent(source_ip="10.0.0.4", event_type="login_failed", raw_message="failed"))
    event = orchestrator.store.all("events")[0]
    assert event["event_type"] == "LOGIN_FAILED"


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_key_manager_rotates_and_isolates_invalid_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY_1", "test-one")
    monkeypatch.setenv("GEMINI_API_KEY_2", "test-two")
    manager = GeminiKeyManager()
    first, second = manager.acquire(), manager.acquire()
    assert [first.identifier, second.identifier] == ["key-01", "key-02"]
    manager.record_failure(first, "authentication")
    assert manager.acquire().identifier == "key-02"
    assert manager.status()["invalid"] == 1


def test_key_manager_cooldown(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY_1", "test-only")
    manager = GeminiKeyManager(cooldown_seconds=60)
    key = manager.acquire()
    manager.record_failure(key, "rate_limit")
    assert manager.acquire() is None
    assert manager.status()["cooldown"] == 1


def test_response_allowlist_rejects_arbitrary_command():
    try:
        ResponseAction(action="rm -rf /", target="host", reason="unsafe")
    except ValidationError:
        return
    raise AssertionError("Unsafe action must not pass the response allowlist")
