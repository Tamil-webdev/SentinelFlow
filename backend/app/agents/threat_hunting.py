from __future__ import annotations

from ..models import SecurityEvent


class ThreatHuntingAgent:
    name = "Threat Hunting Agent"

    def hunt(self, source_ip: str, events: list[SecurityEvent]) -> tuple[list[str], list[SecurityEvent]]:
        related = sorted([event for event in events if event.source_ip == source_ip], key=lambda item: item.timestamp)
        suspicious = [event for event in related if event.event_type != "NORMAL_REQUEST"]
        evidence = [f"Historical search found {len(related)} events from {source_ip}."]
        if len(suspicious) > 1:
            evidence.append(f"{len(suspicious)} events are security-relevant and form an escalation timeline.")
        event_types = sorted({event.event_type for event in suspicious})
        if len(event_types) > 1:
            evidence.append(f"Observed related activity: {', '.join(event_types)}.")
        return evidence, related[-80:]

