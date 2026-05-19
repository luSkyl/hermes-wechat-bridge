"""Event deduplication with retry-safe processing states."""

from __future__ import annotations

import contextlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RECEIVED = "received"
PROCESSING = "processing"
SUCCEEDED = "succeeded"
FAILED = "failed"


@dataclass(frozen=True)
class DedupeClaim:
    """Result of claiming an event for processing."""

    event_id: str
    duplicate: bool
    status: str
    attempts: int = 0


class DedupeStore:
    """TTL-based dedupe store that marks events complete only after success."""

    def __init__(
        self,
        ttl_seconds: int = 300,
        state_dir: str | Path | None = None,
        lock_timeout_seconds: float = 2.0,
        lock_stale_seconds: float = 30.0,
    ) -> None:
        self.ttl_seconds = max(1, ttl_seconds)
        self.state_dir = Path(state_dir).expanduser() if state_dir else None
        self.lock_timeout_seconds = max(0.1, lock_timeout_seconds)
        self.lock_stale_seconds = max(1.0, lock_stale_seconds)
        self._seen: dict[str, dict[str, Any]] = {}
        if self.state_dir is not None:
            self.state_file = self.state_dir / "dedupe-state.json"
            self.lock_file = self.state_dir / "dedupe-state.lock"
        else:
            self.state_file = None
            self.lock_file = None

    def seen(self, event_id: str) -> bool:
        """Compatibility helper: claim and immediately complete new events."""

        claim = self.begin(event_id)
        if claim.duplicate:
            return True
        self.complete(event_id)
        return False

    def begin(self, event_id: str) -> DedupeClaim:
        """Claim an event unless it has already completed successfully."""

        now = time.monotonic()
        with self._locked_state(now) as state:
            self._evict_expired(state, now)
            existing = state.get(event_id)
            if isinstance(existing, dict) and existing.get("status") == SUCCEEDED:
                return DedupeClaim(event_id=event_id, duplicate=True, status=SUCCEEDED, attempts=int(existing.get("attempts") or 0))
            attempts = int(existing.get("attempts") or 0) + 1 if isinstance(existing, dict) else 1
            state[event_id] = {
                "status": PROCESSING,
                "attempts": attempts,
                "updated_at": now,
                "expires_at": now + self.ttl_seconds,
            }
            return DedupeClaim(event_id=event_id, duplicate=False, status=PROCESSING, attempts=attempts)

    def complete(self, event_id: str) -> None:
        now = time.monotonic()
        with self._locked_state(now) as state:
            self._evict_expired(state, now)
            existing = state.get(event_id)
            attempts = int(existing.get("attempts") or 1) if isinstance(existing, dict) else 1
            state[event_id] = {
                "status": SUCCEEDED,
                "attempts": attempts,
                "updated_at": now,
                "expires_at": now + self.ttl_seconds,
            }

    def fail(self, event_id: str, reason: str | None = None) -> None:
        now = time.monotonic()
        with self._locked_state(now) as state:
            self._evict_expired(state, now)
            existing = state.get(event_id)
            attempts = int(existing.get("attempts") or 1) if isinstance(existing, dict) else 1
            state[event_id] = {
                "status": FAILED,
                "attempts": attempts,
                "reason": str(reason or "processing_failed")[:200],
                "updated_at": now,
                "expires_at": now + self.ttl_seconds,
            }

    @contextlib.contextmanager
    def _locked_state(self, now: float):
        if self.state_dir is None:
            yield self._seen
            return
        assert self.lock_file is not None
        with _StateLock(self.lock_file, self.lock_timeout_seconds, self.lock_stale_seconds):
            state = self._load_state(now)
            yield state
            self._save_state(state)

    def _load_state(self, now: float) -> dict[str, dict[str, Any]]:
        assert self.state_file is not None
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            loaded = json.loads(self.state_file.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            loaded = {}
        if not isinstance(loaded, dict):
            return {}
        events = loaded.get("events", loaded)
        if not isinstance(events, dict):
            return {}
        state: dict[str, dict[str, Any]] = {}
        for key, value in events.items():
            if isinstance(key, str) and isinstance(value, dict):
                state[key] = dict(value)
        self._evict_expired(state, now)
        return state

    def _save_state(self, state: dict[str, dict[str, Any]]) -> None:
        assert self.state_file is not None
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"version": 1, "events": state}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        temp_file = self.state_file.with_suffix(f".tmp-{uuid.uuid4().hex}")
        temp_file.write_text(payload, encoding="utf-8")
        temp_file.replace(self.state_file)

    @staticmethod
    def _evict_expired(state: dict[str, dict[str, Any]], now: float) -> None:
        expired = [event_id for event_id, entry in state.items() if float(entry.get("expires_at") or 0.0) <= now]
        for event_id in expired:
            state.pop(event_id, None)


class _StateLock:
    def __init__(self, path: Path, timeout_seconds: float, stale_seconds: float) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds
        self.stale_seconds = stale_seconds
        self.fd: int | None = None

    def __enter__(self) -> _StateLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self.fd, str(os.getpid()).encode("ascii", errors="ignore"))
                return self
            except FileExistsError as exc:
                self._remove_stale_lock()
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out waiting for dedupe lock: {self.path}") from exc
                time.sleep(0.05)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        with contextlib.suppress(OSError):
            self.path.unlink(missing_ok=True)

    def _remove_stale_lock(self) -> None:
        try:
            if time.time() - self.path.stat().st_mtime > self.stale_seconds:
                self.path.unlink(missing_ok=True)
        except OSError:
            pass
