from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import SecurityEvent


class SecurityEventSource(ABC):
    """Adapter contract for optional external security telemetry sources."""

    @abstractmethod
    def normalize(self, record: dict) -> SecurityEvent:
        raise NotImplementedError


class DemoEventSource(SecurityEventSource):
    def normalize(self, record: dict) -> SecurityEvent:
        return SecurityEvent.model_validate(record)


class SuricataAdapter(SecurityEventSource):
    def normalize(self, record: dict) -> SecurityEvent:
        return SecurityEvent(source_ip=record.get("src_ip", "unknown"), destination_ip=record.get("dest_ip", "unknown"), destination_port=record.get("dest_port"), event_type="SURICATA_ALERT", service="suricata", raw_message=str(record), source="suricata")


class ZeekAdapter(SecurityEventSource):
    def normalize(self, record: dict) -> SecurityEvent:
        return SecurityEvent(source_ip=record.get("id.orig_h", "unknown"), destination_ip=record.get("id.resp_h", "unknown"), destination_port=record.get("id.resp_p"), event_type="ZEEK_CONNECTION", service="zeek", raw_message=str(record), source="zeek")


class WazuhAdapter(SecurityEventSource):
    def normalize(self, record: dict) -> SecurityEvent:
        return SecurityEvent(source_ip=record.get("data", {}).get("srcip", "unknown"), event_type="WAZUH_ALERT", service="wazuh", raw_message=str(record), source="wazuh")

