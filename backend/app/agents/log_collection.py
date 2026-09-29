from __future__ import annotations

from ..models import SecurityEvent
from ..store import LocalStore


class LogCollectionAgent:
    name = "Log Collection Agent"

    def __init__(self, store: LocalStore) -> None:
        self.store = store

    def collect(self, event: SecurityEvent) -> SecurityEvent:
        normalized = event.model_copy(update={"event_type": event.event_type.upper(), "severity": event.severity.upper()})
        self.store.add("events", normalized.model_dump(mode="json"))
        return normalized

