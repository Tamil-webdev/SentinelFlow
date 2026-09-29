from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from ..models import Detection, SecurityEvent

class ThreatDetectionAgent:
    name = "Threat Detection Agent"

    def detect(self, event: SecurityEvent, history: list[SecurityEvent]) -> Detection | None:
        window_start = event.timestamp - timedelta(seconds=60)
        related = [item for item in history if item.source_ip == event.source_ip and item.timestamp >= window_start]
        failed_logins = [item for item in related if item.event_type == "LOGIN_FAILED"]
        if event.event_type == "LOGIN_FAILED" and len(failed_logins) >= 20:
            return Detection(
                threat_type="BRUTE_FORCE",
                target=event.username or event.service,
                evidence=[f"{len(failed_logins)} failed login attempts from {event.source_ip} within 60 seconds", f"Targeted account: {event.username or 'unknown'}"],
            )
        ports = {item.destination_port for item in related if item.destination_port is not None}
        if event.event_type in {"CONNECTION_ATTEMPT", "PORT_PROBE"} and len(ports) >= 10:
            return Detection(
                threat_type="PORT_SCAN",
                target=event.destination_ip,
                evidence=[f"{len(ports)} destination ports accessed by {event.source_ip} within 60 seconds", "Rapid multi-port reconnaissance pattern"],
            )
        if event.event_type == "CONTAINER_SUSPICIOUS_ACTIVITY":
            return Detection(
                threat_type="CONTAINER_COMPROMISE",
                target=event.metadata.get("container", "unknown-container"),
                evidence=["Unexpected privileged process activity in container", "Outbound connection to known simulated command-and-control endpoint"],
            )
        return None

