from __future__ import annotations

import time
from datetime import timedelta

from ..models import AgentRun, Incident, SecurityEvent, utc_now
from ..services import GeminiService
from ..store import LocalStore
from .log_collection import LogCollectionAgent
from .report_generation import ReportGenerationAgent
from .response import ResponseAgent
from .risk_assessment import RiskAssessmentAgent
from .threat_detection import ThreatDetectionAgent
from .threat_hunting import ThreatHuntingAgent


class SocOrchestrator:
    def __init__(self, store: LocalStore | None = None) -> None:
        self.store = store or LocalStore()
        self.collection = LogCollectionAgent(self.store)
        self.detection = ThreatDetectionAgent()
        self.hunting = ThreatHuntingAgent()
        self.risk = RiskAssessmentAgent()
        self.response = ResponseAgent()
        self.reporting = ReportGenerationAgent()
        self.ai = GeminiService()

    def _run(self, agent: str, input_id: str, callback):
        started = time.perf_counter()
        result = callback()
        duration = round((time.perf_counter() - started) * 1000, 2)
        if result is None:
            output = "No threat detected"
        elif hasattr(result, "threat_type"):
            output = result.threat_type
        elif hasattr(result, "level") and hasattr(result, "score"):
            output = f"{result.level} risk: {result.score}/100"
        elif hasattr(result, "action"):
            output = result.action
        elif isinstance(result, tuple):
            output = f"{len(result[1])} related events found"
        elif isinstance(result, dict) and result.get("incident_id"):
            output = "Structured report generated"
        elif hasattr(result, "event_type"):
            output = f"Normalized {result.event_type}"
        else:
            output = "Completed"
        self.store.add("agent_runs", AgentRun(agent=agent, input_id=input_id, output=output, duration_ms=duration).model_dump(mode="json"))
        return result

    def _ai_summary(self, agent: str, input_id: str, facts: dict):
        outcome = self.ai.summarize(agent, facts)
        output = outcome.value.summary if outcome.value else f"AI fallback: {outcome.error_type or 'unavailable'}"
        self.store.add("agent_runs", AgentRun(agent=agent, input_id=input_id, output=output, duration_ms=outcome.latency_ms, model=outcome.model, key_identifier=outcome.key_id, error_type=outcome.error_type).model_dump(mode="json"))
        return outcome

    def process_event(self, event: SecurityEvent) -> Incident | None:
        normalized = self._run(self.collection.name, event.id, lambda: self.collection.collect(event))
        events = [SecurityEvent.model_validate(item) for item in self.store.all("events")]
        detection = self._run(self.detection.name, normalized.id, lambda: self.detection.detect(normalized, events))
        if not detection:
            return None
        existing = next((item for item in self.incidents() if item["threat_type"] == detection.threat_type and item["source_ip"] == normalized.source_ip), None)
        if existing:
            return None
        detection_ai = self._ai_summary(self.detection.name, normalized.id, {"threat_type": detection.threat_type, "source_ip": normalized.source_ip, "target": detection.target, "evidence": detection.evidence})
        if detection_ai.value:
            detection.evidence.append(f"AI analysis: {detection_ai.value.summary}")
        hunting_evidence, timeline = self._run(self.hunting.name, normalized.id, lambda: self.hunting.hunt(normalized.source_ip, events))
        hunting_ai = self._ai_summary(self.hunting.name, normalized.id, {"source_ip": normalized.source_ip, "event_ids": [item.id for item in timeline], "event_types": [item.event_type for item in timeline], "hunting_evidence": hunting_evidence})
        if hunting_ai.value:
            hunting_evidence.append(f"AI analysis: {hunting_ai.value.summary}")
        risk = self._run(self.risk.name, normalized.id, lambda: self.risk.assess(detection.threat_type, timeline, detection.target))
        response = self._run(self.response.name, normalized.id, lambda: self.response.respond(detection.threat_type, risk.level, normalized.source_ip, detection.target))
        status = "CONTAINED" if response.action != "MONITOR" else "MONITORING"
        incident = Incident(
            threat_type=detection.threat_type, detection_method=detection.method, source_ip=normalized.source_ip, target=detection.target,
            event_ids=[item.id for item in timeline], risk=risk, detection_evidence=detection.evidence,
            hunting_evidence=hunting_evidence, timeline=timeline, response=response, status=status,
        )
        report = self._run(self.reporting.name, incident.id, lambda: self.reporting.generate(incident))
        report_ai = self._ai_summary(self.reporting.name, incident.id, {"incident_id": incident.id, "threat_type": incident.threat_type, "source_ip": incident.source_ip, "target": incident.target, "risk": risk.model_dump(), "response": response.model_dump(mode="json"), "evidence": incident.detection_evidence + incident.hunting_evidence})
        if report_ai.value:
            report["ai_summary"] = report_ai.value.summary
            report["recommendations"] = report_ai.value.recommendations
        incident.report = report
        self.store.add("incidents", incident.model_dump(mode="json"))
        self.store.add("responses", response.model_dump(mode="json"))
        self.store.add("reports", report)
        return incident

    def incidents(self) -> list[dict]:
        return sorted(self.store.all("incidents"), key=lambda item: item["created_at"], reverse=True)

    def metrics(self) -> dict:
        events = self.store.all("events")
        incidents = self.incidents()
        responses = self.store.all("responses")
        ai = self.ai.status()
        return {
            "events_processed_total": len(events), "threats_detected_total": len(incidents), "incidents_created_total": len(incidents),
            "responses_executed_total": len(responses), "blocked_ips": len({item["target"] for item in responses if item["action"] == "BLOCK_IP"}),
            "active_threats": len([item for item in incidents if item["status"] == "OPEN"]),
            "critical_incidents": len([item for item in incidents if item["risk"]["level"] == "CRITICAL"]),
            "high_incidents": len([item for item in incidents if item["risk"]["level"] == "HIGH"]),
            "detection_latency_ms": 0, "response_latency_ms": 0, "gemini_requests_total": ai["requests"],
            "gemini_success_total": ai["successes"], "gemini_failures_total": ai["failures"],
            "gemini_key_cooldowns_total": ai["cooldown"],
        }

    def agent_status(self) -> list[dict]:
        runs = self.store.all("agent_runs")
        names = [self.collection.name, self.detection.name, self.hunting.name, self.risk.name, self.response.name, self.reporting.name]
        result = []
        for name in names:
            matching = [run for run in runs if run["agent"] == name]
            last = matching[-1] if matching else None
            result.append({"name": name, "status": "ready", "processed": len(matching), "last_execution": last["completed_at"] if last else None, "average_duration_ms": round(sum(float(run["duration_ms"]) for run in matching) / len(matching), 2) if matching else 0, "last_decision": last["output"] if last else "Awaiting events", "model": last.get("model") if last else None, "key_identifier": last.get("key_identifier") if last else None, "last_error": last.get("error_type") if last else None})
        return result
