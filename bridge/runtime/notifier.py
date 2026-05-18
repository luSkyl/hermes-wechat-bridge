"""Notification sending facade with Weixin delivery governance.

This module is the open-source equivalent of the local ``send_message_tool``
notification path: every notification is rendered as a friendly card, admitted
through the Weixin governor, and either delivered, queued, or safely summarized.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from bridge.protocol import DeliveryRequest, DeliveryResult
from bridge.runtime.friendly_card import ensure_friendly_card, friendly_card
from bridge.wechat.sender import WeChatSender


@dataclass(frozen=True)
class Notification:
    """A user-visible notification that must be delivered as a friendly card."""

    target_id: str
    title: str
    summary: str
    source: str = "notification"
    severity: str = "info"
    priority: str = "normal"
    sections: tuple[tuple[str, str | Iterable[str]], ...] = ()
    actions: tuple[str, ...] = ("无需操作，我会继续跟进。",)
    conversation_id: str = "notification"
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        return friendly_card(
            title=self.title,
            summary=self.summary,
            severity=self.severity,
            sections=self.sections,
            actions=self.actions,
            metadata=self.metadata,
        )

    def to_request(self) -> DeliveryRequest:
        metadata = {
            "source": self.source,
            "priority": self.priority,
            "friendly_card": True,
            **self.metadata,
        }
        return DeliveryRequest(
            conversation_id=self.conversation_id,
            recipient_id=self.target_id,
            text=self.render(),
            metadata=metadata,
        )


class BridgeNotifier:
    """High-level governed notification sender."""

    def __init__(self, sender: WeChatSender) -> None:
        self.sender = sender

    def notify(self, notification: Notification) -> DeliveryResult:
        """Send or queue a friendly notification."""

        result = self.sender.send(notification.to_request())
        return _attach_user_message(result)

    def notify_text(
        self,
        *,
        target_id: str,
        text: str,
        title: str = "通知已接收",
        source: str = "notification",
        priority: str = "normal",
        severity: str = "info",
        conversation_id: str = "notification",
        metadata: dict[str, Any] | None = None,
    ) -> DeliveryResult:
        """Wrap raw text into the friendly-card contract and send it."""

        card = ensure_friendly_card(text, title=title, severity=severity)
        request = DeliveryRequest(
            conversation_id=conversation_id,
            recipient_id=target_id,
            text=card,
            metadata={
                "source": source,
                "priority": priority,
                "friendly_card": True,
                **dict(metadata or {}),
            },
        )
        return _attach_user_message(self.sender.send(request))

    def flush_queued(self, *, target_id: str, limit: int | None = None) -> list[DeliveryResult]:
        """Attempt to drain queued notifications for a target."""

        return [_attach_user_message(item) for item in self.sender.flush_queued(target_id=target_id, limit=limit)]

    def status(self) -> dict[str, Any]:
        """Return the delivery governor status for dashboards or CLIs."""

        return self.sender.governor.status()


def _attach_user_message(result: DeliveryResult) -> DeliveryResult:
    metadata = dict(result.metadata)
    if metadata.get("user_message") and not metadata.get("queued"):
        return result
    if metadata.get("queued"):
        governor = metadata.get("governor") if isinstance(metadata.get("governor"), dict) else metadata
        metadata["user_message"] = friendly_card(
            title="微信通知已进入补发队列",
            summary="这次没有继续打扰微信发送通道，通知会在后续窗口补发。",
            severity="warning",
            sections=(
                ("原因", str(metadata.get("reason") or governor.get("reason") or "delivery_governed")),
                ("队列", f"当前约 {governor.get('queue_size', metadata.get('queue_size', '未知'))} 条待补发"),
            ),
            actions=("请在 Web UI 或本地日志查看即时状态。", "我会在可发送窗口自动 flush。"),
        )
    elif not result.ok:
        metadata["user_message"] = friendly_card(
            title="微信通知发送失败",
            summary="通知未送达微信，但已经生成安全摘要。",
            severity="error",
            sections=(("原因", result.error or "unknown"),),
            actions=("请检查发送适配器、凭据和网络。",),
        )
    return DeliveryResult(
        ok=result.ok,
        delivery_id=result.delivery_id,
        error=result.error,
        attempts=result.attempts,
        metadata=metadata,
    )

