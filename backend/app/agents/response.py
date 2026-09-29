from __future__ import annotations

from ..config import settings
from ..models import ResponseAction


class ResponseAgent:
    name = "Response Agent"

    def respond(self, threat_type: str, risk_level: str, source_ip: str, target: str) -> ResponseAction:
        action = "MONITOR"
        action_target = source_ip
        if threat_type == "CONTAINER_COMPROMISE" and risk_level == "CRITICAL":
            action, action_target = "QUARANTINE_CONTAINER", target
        elif threat_type == "BRUTE_FORCE" and risk_level in {"HIGH", "CRITICAL"}:
            action = "BLOCK_IP"
        elif threat_type == "PORT_SCAN" and risk_level in {"MEDIUM", "HIGH", "CRITICAL"}:
            action = "BLOCK_IP"
        status = "simulated" if settings.response_mode == "simulation" else "not_required"
        return ResponseAction(action=action, target=action_target, reason=f"{risk_level} {threat_type} incident", status=status, mode=settings.response_mode)

