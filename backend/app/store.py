from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any

from .config import settings


class LocalStore:
    """Small Firestore-compatible document-store fallback for demo mode."""

    collections = ("events", "incidents", "agent_runs", "responses", "reports")

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._documents: dict[str, list[dict[str, Any]]] = {name: self._load(name) for name in self.collections}

    def _path(self, collection: str) -> Path:
        return self.data_dir / f"{collection}.json"

    def _load(self, collection: str) -> list[dict[str, Any]]:
        path = self._path(collection)
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save(self, collection: str) -> None:
        self._path(collection).write_text(json.dumps(self._documents[collection], indent=2, default=str), encoding="utf-8")

    def add(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._documents[collection].append(document)
            self._save(collection)
        return document

    def all(self, collection: str) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._documents[collection])

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        with self._lock:
            return next((item for item in self._documents[collection] if item.get("id") == document_id), None)

    def replace(self, collection: str, document_id: str, document: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            for index, item in enumerate(self._documents[collection]):
                if item.get("id") == document_id:
                    self._documents[collection][index] = document
                    self._save(collection)
                    return document
        return self.add(collection, document)

