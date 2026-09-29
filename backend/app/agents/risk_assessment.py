from __future__ import annotations

from ..models import RiskAssessment, SecurityEvent


class RiskAssessmentAgent:
    name = "Risk Assessment Agent"

    def assess(self, threat_type: str, timeline: list[SecurityEvent], target: str) -> RiskAssessment:
        factors: list[dict[str, int | str]] = []
        if threat_type == "BRUTE_FORCE":
            attempts = sum(event.event_type == "LOGIN_FAILED" for event in timeline)
            factors += [{"factor": f"{attempts} repeated failed logins", "weight": 38}, {"factor": "Credential attack pattern", "weight": 22}]
            if target.lower() in {"admin", "root", "administrator"}:
                factors.append({"factor": "Privileged target account", "weight": 18})
        elif threat_type == "PORT_SCAN":
            factors += [{"factor": "Rapid multi-port reconnaissance", "weight": 34}, {"factor": "Multiple exposed services targeted", "weight": 18}]
        elif threat_type == "CONTAINER_COMPROMISE":
            factors += [{"factor": "Suspicious privileged container activity", "weight": 50}, {"factor": "Potential command-and-control communication", "weight": 31}]
        if len(timeline) > 20:
            factors.append({"factor": "High event volume", "weight": 12})
        if len({event.event_type for event in timeline}) > 1:
            factors.append({"factor": "Historical suspicious activity", "weight": 10})
        score = min(100, sum(int(item["weight"]) for item in factors))
        level = "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MEDIUM" if score >= 31 else "LOW"
        return RiskAssessment(score=score, level=level, factors=factors)
