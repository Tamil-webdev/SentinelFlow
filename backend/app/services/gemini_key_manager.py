from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KeyState:
    identifier: str
    value: str
    status: str = "healthy"
    cooldown_until: float = 0
    requests: int = 0
    successes: int = 0
    failures: int = 0


class GeminiKeyManager:
    """Health-aware credential pool. Credential values never leave this class."""

    def __init__(self, key_file: str = "", cooldown_seconds: int = 60) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._cursor = 0
        self.keys = [KeyState(f"key-{index:02d}", key) for index, key in enumerate(self._load_keys(key_file), start=1)]

    def _load_keys(self, key_file: str) -> list[str]:
        values = [value.strip() for name, value in os.environ.items() if re.fullmatch(r"GEMINI_API_KEY(?:_\d+)?", name) and value.strip()]
        if key_file and Path(key_file).is_file():
            for line in Path(key_file).read_text(encoding="utf-8").splitlines():
                candidate = line.strip()
                if "=" in candidate:
                    candidate = candidate.split("=", 1)[1].strip()
                if candidate and not candidate.startswith("#"):
                    values.append(candidate)
        return list(dict.fromkeys(values))

    def acquire(self) -> KeyState | None:
        now = time.monotonic()
        for key in self.keys:
            if key.status == "cooldown" and key.cooldown_until <= now:
                key.status = "healthy"
        eligible = [key for key in self.keys if key.status == "healthy"]
        if not eligible:
            return None
        key = eligible[self._cursor % len(eligible)]
        self._cursor = (self._cursor + 1) % len(eligible)
        key.requests += 1
        return key

    def record_success(self, key: KeyState) -> None:
        key.successes += 1
        key.status = "healthy"

    def record_failure(self, key: KeyState, error_type: str) -> None:
        key.failures += 1
        if error_type == "authentication":
            key.status = "invalid"
        elif error_type in {"rate_limit", "transient", "timeout"}:
            key.status = "cooldown"
            key.cooldown_until = time.monotonic() + self.cooldown_seconds

    def status(self) -> dict:
        counts = {name: sum(key.status == name for key in self.keys) for name in ("healthy", "cooldown", "invalid")}
        return {"configured": bool(self.keys), "total_keys": len(self.keys), **counts, "requests": sum(key.requests for key in self.keys), "successes": sum(key.successes for key in self.keys), "failures": sum(key.failures for key in self.keys), "keys": [{"id": key.identifier, "status": key.status} for key in self.keys]}
