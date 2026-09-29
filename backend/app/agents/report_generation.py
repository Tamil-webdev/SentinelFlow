from __future__ import annotations

from ..models import Incident


class ReportGenerationAgent:
    name = "Report Generation Agent"

    def generate(self, incident: Incident) -> dict:
        action = incident.response.action.replace("_", " ") if incident.response else "No action"
        report = {
            "id": f"RPT-{incident.id[4:]}", "incident_id": incident.id, "generated_at": incident.updated_at,
            "summary": f"{incident.threat_type.replace('_', ' ').title()} from {incident.source_ip} was assessed as {incident.risk.level} risk and {action.lower()}.",
            "human_readable": "\n".join([
                f"Incident: {incident.id}", f"Threat: {incident.threat_type}", f"Source: {incident.source_ip}",
                f"Target: {incident.target}", f"Risk: {incident.risk.level} ({incident.risk.score}/100)",
                f"Response: {action}", f"Status: {incident.status}", "Evidence:", *[f"- {item}" for item in incident.detection_evidence + incident.hunting_evidence],
            ]),
        }
        return report

