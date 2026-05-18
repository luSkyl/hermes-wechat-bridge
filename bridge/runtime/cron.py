"""Portable Cron notification adapter for Hermes WeChat Bridge.

This does not impose a scheduler.  It provides the missing governed delivery
contract that a scheduler can call when a job fails, recovers, or needs to report
queued delivery state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bridge.protocol import DeliveryResult
from bridge.runtime.friendly_card import cron_failure_card, cron_recovery_card
from bridge.runtime.notifier import BridgeNotifier


@dataclass(frozen=True)
class CronJobNotice:
    """A user-visible notice emitted by a Cron scheduler."""

    target_id: str
    job_name: str
    reason: str = ""
    next_run: str | None = None
    priority: str = "high"
    metadata: dict[str, Any] = field(default_factory=dict)


class CronDeliveryNotifier:
    """Governed Cron failure/recovery delivery helper."""

    def __init__(self, notifier: BridgeNotifier) -> None:
        self.notifier = notifier

    def failure(self, notice: CronJobNotice) -> DeliveryResult:
        text = cron_failure_card(job_name=notice.job_name, reason=notice.reason, next_run=notice.next_run)
        return self.notifier.notify_text(
            target_id=notice.target_id,
            text=text,
            title="定时任务需要关注",
            source="cron",
            priority=notice.priority,
            severity="warning",
            conversation_id=f"cron:{notice.job_name}",
            metadata={"cron_job": notice.job_name, **notice.metadata},
        )

    def recovery(self, notice: CronJobNotice) -> DeliveryResult:
        text = cron_recovery_card(job_name=notice.job_name, detail=notice.reason or "任务已恢复正常。")
        return self.notifier.notify_text(
            target_id=notice.target_id,
            text=text,
            title="定时任务已恢复",
            source="cron",
            priority=notice.priority,
            severity="success",
            conversation_id=f"cron:{notice.job_name}",
            metadata={"cron_job": notice.job_name, **notice.metadata},
        )

    def flush(self, *, target_id: str, limit: int | None = None) -> list[DeliveryResult]:
        return self.notifier.flush_queued(target_id=target_id, limit=limit)
