from __future__ import annotations

from datetime import timedelta
from random import randint

from .agents.orchestrator import SocOrchestrator
from .models import SecurityEvent, utc_now


def brute_force(orchestrator: SocOrchestrator):
    ip, account, now = "185.220.101.77", "admin", utc_now()
    incident = None
    for index in range(randint(35, 50)):
        incident = orchestrator.process_event(SecurityEvent(timestamp=now + timedelta(seconds=index), source_ip=ip, event_type="LOGIN_FAILED", username=account, service="identity-api", severity="medium", raw_message=f"Authentication failed for {account} from {ip}")) or incident
    return incident


def port_scan(orchestrator: SocOrchestrator):
    ip, now, incident = "45.83.64.19", utc_now(), None
    for index, port in enumerate([21, 22, 23, 25, 53, 80, 110, 443, 445, 3306, 5432, 8080]):
        incident = orchestrator.process_event(SecurityEvent(timestamp=now + timedelta(seconds=index), source_ip=ip, event_type="PORT_PROBE", destination_port=port, service="edge-gateway", severity="low", raw_message=f"Connection probe from {ip} to port {port}")) or incident
    return incident


def container_attack(orchestrator: SocOrchestrator):
    event = SecurityEvent(source_ip="10.42.2.88", event_type="CONTAINER_SUSPICIOUS_ACTIVITY", service="payments-api", severity="critical", raw_message="Unexpected privileged process spawned inside payments-api", metadata={"container": "payments-api-7f8c9d"})
    return orchestrator.process_event(event)


def normal_traffic(orchestrator: SocOrchestrator):
    events = []
    for index in range(12):
        event = SecurityEvent(source_ip=f"10.0.1.{20 + index}", event_type="NORMAL_REQUEST", service="web-api", severity="info", raw_message="Successful application request")
        orchestrator.process_event(event)
        events.append(event)
    return events

