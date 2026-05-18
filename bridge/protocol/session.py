"""Session protocol for mapping WeChat conversations to Hermes sessions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionRef:
    """A stable bridge session reference."""

    session_id: str
    platform: str
    conversation_id: str
    sender_id: str

    @classmethod
    def from_message(cls, platform: str, conversation_id: str, sender_id: str) -> SessionRef:
        safe_platform = platform.strip().lower() or "wechat"
        safe_conversation = conversation_id.strip() or "unknown-conversation"
        safe_sender = sender_id.strip() or "unknown-sender"
        return cls(
            session_id=f"{safe_platform}:{safe_conversation}:{safe_sender}",
            platform=safe_platform,
            conversation_id=safe_conversation,
            sender_id=safe_sender,
        )
