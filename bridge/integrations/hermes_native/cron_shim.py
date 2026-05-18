"""Cron notification shim for Hermes-native integrations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bridge.runtime.config import load_config
from bridge.runtime.cron import CronDeliveryNotifier, CronJobNotice
from bridge.runtime.notifier import BridgeNotifier
from bridge.wechat import WeChatSender


def notify_cron_failure(
    *,
    config_path: str | Path,
    target_id: str,
    job_name: str,
    reason: str,
    next_run: str | None = None,
    priority: str = "high",
    metadata: dict[str, Any] | None = None,
) -> dict[str, object]:
    notifier = _cron_notifier(config_path)
    result = notifier.failure(
        CronJobNotice(
            target_id=target_id,
            job_name=job_name,
            reason=reason,
            next_run=next_run,
            priority=priority,
            metadata=dict(metadata or {}),
        )
    )
    return result.to_dict()


def notify_cron_recovery(
    *,
    config_path: str | Path,
    target_id: str,
    job_name: str,
    detail: str = "任务已恢复正常。",
    priority: str = "high",
    metadata: dict[str, Any] | None = None,
) -> dict[str, object]:
    notifier = _cron_notifier(config_path)
    result = notifier.recovery(
        CronJobNotice(
            target_id=target_id,
            job_name=job_name,
            reason=detail,
            priority=priority,
            metadata=dict(metadata or {}),
        )
    )
    return result.to_dict()


def _cron_notifier(config_path: str | Path) -> CronDeliveryNotifier:
    config = load_config(config_path)
    return CronDeliveryNotifier(BridgeNotifier(WeChatSender(config.wechat)))
