from __future__ import annotations

import random
from datetime import timedelta
from uuid import uuid4

from .agents.orchestrator import SocOrchestrator
from .models import SecurityEvent, utc_now

def generate_ip():
    return f"{random.randint(11, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"

def format_response(simulation: str, events: list[SecurityEvent], incident=None):
    if incident:
        return {
            "success": True,
            "simulation": simulation,
            "event_id": events[0].id if events else None,
            "incident_id": incident.id,
            "threat_detected": True,
            "risk_level": incident.risk.level,
            "risk_score": incident.risk.score,
            "response_action": incident.response.action if incident.response else "MONITOR",
            "response_status": incident.response.status if incident.response else "simulated",
            "processing_status": "completed",
            "id": incident.id  # For frontend selected handling
        }
    return {
        "success": True,
        "simulation": simulation,
        "event_id": events[0].id if events else None,
        "incident_id": None,
        "threat_detected": False,
        "processing_status": "completed"
    }

def brute_force(orchestrator: SocOrchestrator):
    ip, account, now = generate_ip(), f"admin_{random.randint(100, 999)}", utc_now()
    incident = None
    events = []
    for index in range(random.randint(35, 50)):
        event = SecurityEvent(timestamp=now + timedelta(seconds=index), source_ip=ip, event_type="LOGIN_FAILED", username=account, service="identity-api", severity="medium", raw_message=f"Authentication failed for {account} from {ip}")
        incident = orchestrator.process_event(event) or incident
        events.append(event)
    return format_response("bruteforce", events, incident)


def port_scan(orchestrator: SocOrchestrator):
    ip, now, incident = generate_ip(), utc_now(), None
    events = []
    for index, port in enumerate([21, 22, 23, 25, 53, 80, 110, 443, 445, 3306, 5432, 8080]):
        event = SecurityEvent(timestamp=now + timedelta(seconds=index), source_ip=ip, event_type="PORT_PROBE", destination_port=port, service="edge-gateway", severity="low", raw_message=f"Connection probe from {ip} to port {port}")
        incident = orchestrator.process_event(event) or incident
        events.append(event)
    return format_response("port-scan", events, incident)


def container_attack(orchestrator: SocOrchestrator):
    ip = f"10.42.{random.randint(1, 10)}.{random.randint(1, 254)}"
    container = f"payments-api-{uuid4().hex[:6]}"
    event = SecurityEvent(source_ip=ip, event_type="CONTAINER_SUSPICIOUS_ACTIVITY", service="payments-api", severity="critical", raw_message=f"Unexpected privileged process spawned inside payments-api", metadata={"container": container})
    incident = orchestrator.process_event(event)
    return format_response("container-attack", [event], incident)


def normal_traffic(orchestrator: SocOrchestrator):
    events = []
    now = utc_now()
    for index in range(12):
        ip = f"10.0.{random.randint(1, 5)}.{random.randint(10, 250)}"
        event = SecurityEvent(timestamp=now + timedelta(seconds=index), source_ip=ip, event_type="NORMAL_REQUEST", service="web-api", severity="info", raw_message="Successful application request")
        orchestrator.process_event(event)
        events.append(event)
    return format_response("normal-traffic", events, None)

