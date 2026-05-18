"""Health and diagnostics models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HealthCheckResult:
    ok: bool
    checks: dict[str, bool]
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "checks": self.checks, "messages": self.messages}
