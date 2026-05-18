"""Message protocol shared by the adapter and runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MessageKind(StrEnum):
    """Supported inbound message kinds."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    COMMAND = "command"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Attachment:
    """A normalized inbound attachment."""

    attachment_id: str
    kind: str
    name: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "attachment_id": self.attachment_id,
            "kind": self.kind,
            "name": self.name,
            "url": self.url,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class MessageEvent:
    """A normalized inbound message from WeChat."""

    event_id: str
    platform: str
    conversation_id: str
    sender_id: str
    kind: MessageKind
    text: str = ""
    timestamp: int | None = None
    reply_to: str | None = None
    attachments: tuple[Attachment, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)

    def prompt_text(self) -> str:
        if self.kind == MessageKind.COMMAND:
            return self.text.strip()
        if self.text.strip():
            return self.text.strip()
        if self.attachments:
            names = ", ".join(item.name or item.attachment_id for item in self.attachments)
            return f"User sent {len(self.attachments)} attachment(s): {names}"
        return "User sent an empty or unsupported message."

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "platform": self.platform,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "kind": self.kind.value,
            "text": self.text,
            "timestamp": self.timestamp,
            "reply_to": self.reply_to,
            "attachments": [item.to_dict() for item in self.attachments],
            "raw": self.raw,
        }


@dataclass(frozen=True)
class HermesResponse:
    """A normalized response from Hermes Agent."""

    text: str
    session_id: str
    ok: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "session_id": self.session_id,
            "ok": self.ok,
            "error": self.error,
            "metadata": self.metadata,
        }
