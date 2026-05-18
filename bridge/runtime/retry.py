"""Retry helpers."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

ResultT = TypeVar("ResultT")


def retry_call(action: Callable[[], ResultT], attempts: int, backoff_seconds: float) -> tuple[ResultT, int]:
    total_attempts = max(1, attempts)
    last_error: Exception | None = None
    for attempt in range(1, total_attempts + 1):
        try:
            return action(), attempt
        except Exception as error:  # noqa: BLE001 - preserve last expected bridge failure for caller
            last_error = error
            if attempt < total_attempts and backoff_seconds > 0:
                time.sleep(backoff_seconds)
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_call exhausted without result or error")
