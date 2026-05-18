"""In-memory event deduplication."""

from __future__ import annotations

import time


class DedupeStore:
    """Small TTL-based dedupe store for webhook event IDs."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = max(1, ttl_seconds)
        self._seen: dict[str, float] = {}

    def seen(self, event_id: str) -> bool:
        now = time.monotonic()
        self._evict_expired(now)
        if event_id in self._seen:
            return True
        self._seen[event_id] = now + self.ttl_seconds
        return False

    def _evict_expired(self, now: float) -> None:
        expired = [event_id for event_id, expires_at in self._seen.items() if expires_at <= now]
        for event_id in expired:
            self._seen.pop(event_id, None)
