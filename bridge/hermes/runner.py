"""Helpers for future Hermes process management."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HermesRunnerState:
    available: bool
    mode: str
    detail: str
