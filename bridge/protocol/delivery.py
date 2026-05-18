"""Outbound delivery protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DeliveryRequest:
    """A request to deliver a message back to WeChat."""

    conversation_id: str
    recipient_id: str
    text: str
    reply_to: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "recipient_id": self.recipient_id,
            "text": self.text,
            "reply_to": self.reply_to,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class DeliveryResult:
    """Result of an outbound delivery attempt."""

    ok: bool
    delivery_id: str | None = None
    error: str | None = None
    attempts: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "delivery_id": self.delivery_id,
            "error": self.error,
            "attempts": self.attempts,
            "metadata": self.metadata,
        }
