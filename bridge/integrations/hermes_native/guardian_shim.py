"""Guardian/watchdog notification shim for Hermes-native integrations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bridge.runtime.config import load_config
from bridge.runtime.guardian import GuardianDeliveryNotifier, GuardianIncident
from bridge.runtime.notifier import BridgeNotifier
from bridge.wechat import WeChatSender


def notify_guardian_incident(
    *,
    config_path: str | Path,
    target_id: str,
    name: str,
    state: str,
    reason: str,
    action: str | None = None,
    priority: str = "critical",
    metadata: dict[str, Any] | None = None,
) -> dict[str, object]:
    notifier = _guardian_notifier(config_path)
    result = notifier.incident(
        GuardianIncident(
            target_id=target_id,
            name=name,
            state=state,
            reason=reason,
            action=action,
            priority=priority,
            metadata=dict(metadata or {}),
        )
    )
    return result.to_dict()


def notify_guardian_recovery(
    *,
    config_path: str | Path,
    target_id: str,
    name: str,
    detail: str = "链路已恢复。",
    metadata: dict[str, Any] | None = None,
) -> dict[str, object]:
    notifier = _guardian_notifier(config_path)
    result = notifier.recovery(
        GuardianIncident(
            target_id=target_id,
            name=name,
            state="recovered",
            reason=detail,
            metadata=dict(metadata or {}),
        ),
        detail=detail,
    )
    return result.to_dict()


def _guardian_notifier(config_path: str | Path) -> GuardianDeliveryNotifier:
    config = load_config(config_path)
    return GuardianDeliveryNotifier(BridgeNotifier(WeChatSender(config.wechat)))
