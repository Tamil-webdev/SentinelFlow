from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from ..config import settings
from .gemini_key_manager import GeminiKeyManager


class SecurityNarrative(BaseModel):
    summary: str
    recommendations: list[str] = []


@dataclass
class AiOutcome:
    value: SecurityNarrative | None
    model: str | None = None
    key_id: str | None = None
    error_type: str | None = None
    latency_ms: float = 0


class GeminiService:
    def __init__(self, manager: GeminiKeyManager | None = None) -> None:
        self.manager = manager or GeminiKeyManager(settings.gemini_key_file, settings.gemini_key_cooldown_seconds)
        self.last_error: str | None = None
        self.last_success_at: float | None = None

    def _classify_error(self, error: Exception) -> str:
        message = str(error).lower()
        if any(token in message for token in ("401", "403", "api key", "authentication", "permission")):
            return "authentication"
        if "429" in message or "resource_exhausted" in message or "rate limit" in message:
            return "rate_limit"
        if "timeout" in message:
            return "timeout"
        return "transient"

    def summarize(self, agent_name: str, facts: dict[str, Any]) -> AiOutcome:
        if settings.ai_mode == "mock":
            return AiOutcome(SecurityNarrative(summary="Deterministic fallback mode is active; conclusions are based on recorded evidence.", recommendations=[]), model="mock")
        if not settings.gemini_model:
            return AiOutcome(None, error_type="not_configured")
        started = time.perf_counter()
        for attempt in range(settings.gemini_max_retries + 1):
            key = self.manager.acquire()
            if not key:
                return AiOutcome(None, error_type="unavailable", latency_ms=round((time.perf_counter() - started) * 1000, 2))
            try:
                from google import genai
                from google.genai import types

                prompt = "Summarize only the supplied security facts. Do not invent events, IPs, actions, or timestamps. Return concise analyst-facing findings.\n" + json.dumps(facts, default=str)
                client = genai.Client(api_key=key.value)
                response = client.models.generate_content(model=settings.gemini_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=SecurityNarrative, temperature=0))
                parsed = response.parsed if isinstance(response.parsed, SecurityNarrative) else SecurityNarrative.model_validate_json(response.text)
                self.manager.record_success(key)
                self.last_success_at = time.time()
                self.last_error = None
                return AiOutcome(parsed, model=settings.gemini_model, key_id=key.identifier, latency_ms=round((time.perf_counter() - started) * 1000, 2))
            except Exception as error:
                error_type = self._classify_error(error)
                self.manager.record_failure(key, error_type)
                self.last_error = error_type
                if error_type == "authentication" or attempt >= settings.gemini_max_retries:
                    return AiOutcome(None, model=settings.gemini_model, key_id=key.identifier, error_type=error_type, latency_ms=round((time.perf_counter() - started) * 1000, 2))
                time.sleep(min(2, (0.25 * (2 ** attempt)) + random.random() / 10))
        return AiOutcome(None, error_type="unavailable")

    def status(self) -> dict:
        state = self.manager.status()
        return {"provider": "Gemini", "mode": settings.ai_mode, "model": settings.gemini_model or None, "last_error": self.last_error, "last_success_at": self.last_success_at, **state}
