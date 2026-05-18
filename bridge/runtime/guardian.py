"""Portable Guardian notification adapter for Hermes WeChat Bridge.

Guardian itself is not a Hermes upstream primitive.  This adapter extracts the
open-source part that users need: incident and recovery notifications that are
friendly-card formatted and governed before any Weixin send attempt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bridge.protocol import DeliveryResult
from bridge.runtime.friendly_card import guardian_incident_card, guardian_recovery_card
from bridge.runtime.notifier import BridgeNotifier


@dataclass(frozen=True)
class GuardianIncident:
    """A user-visible incident emitted by a watchdog/guardian process."""

    target_id: str
    name: str
    state: str
    reason: str
    action: str | None = None
    priority: str = "critical"
    metadata: dict[str, Any] = field(default_factory=dict)


class GuardianDeliveryNotifier:
    """Governed Guardian incident/recovery delivery helper."""

    def __init__(self, notifier: BridgeNotifier) -> None:
        self.notifier = notifier

    def incident(self, incident: GuardianIncident) -> DeliveryResult:
        text = guardian_incident_card(
            name=incident.name,
            state=incident.state,
            reason=incident.reason,
            action=incident.action,
        )
        return self.notifier.notify_text(
            target_id=incident.target_id,
            text=text,
            title="守护进程发现异常",
            source="guardian",
            priority=incident.priority,
            severity="critical",
            conversation_id=f"guardian:{incident.name}",
            metadata={"guardian_name": incident.name, "guardian_state": incident.state, **incident.metadata},
        )

    def recovery(self, incident: GuardianIncident, *, detail: str = "链路已恢复。") -> DeliveryResult:
        text = guardian_recovery_card(name=incident.name, detail=detail)
        return self.notifier.notify_text(
            target_id=incident.target_id,
            text=text,
            title="守护进程已恢复",
            source="guardian",
            priority="high",
            severity="success",
            conversation_id=f"guardian:{incident.name}",
            metadata={"guardian_name": incident.name, "guardian_state": "recovered", **incident.metadata},
        )

    def flush(self, *, target_id: str, limit: int | None = None) -> list[DeliveryResult]:
        return self.notifier.flush_queued(target_id=target_id, limit=limit)
