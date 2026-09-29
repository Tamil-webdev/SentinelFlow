from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    response_mode = os.getenv("RESPONSE_MODE", "simulation").lower()
    data_dir = Path(os.getenv("SOC_DATA_DIR", "./data"))
    cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    ai_mode = os.getenv("AI_MODE", "gemini").lower()
    gemini_key_file = os.getenv("GEMINI_KEY_FILE", "")
    gemini_model = os.getenv("GEMINI_MODEL", "")
    gemini_max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
    gemini_key_cooldown_seconds = int(os.getenv("GEMINI_KEY_COOLDOWN_SECONDS", "60"))
    gemini_request_timeout = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "20"))


settings = Settings()
