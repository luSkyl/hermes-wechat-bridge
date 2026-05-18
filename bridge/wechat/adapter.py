"""WeChat inbound adapter."""

from __future__ import annotations

from typing import Any

from bridge.protocol import Attachment, MessageEvent, MessageKind, VerificationError
from bridge.runtime.config import WeChatConfig
from bridge.wechat.verifier import verify_signature


class WeChatAdapter:
    """Convert WeChat webhook payloads into bridge protocol events."""

    def __init__(self, config: WeChatConfig) -> None:
        self.config = config

    def verify(self, timestamp: str, nonce: str, signature: str) -> None:
        if not verify_signature(self.config.token, timestamp, nonce, signature):
            raise VerificationError("Invalid WeChat signature")

    def normalize(self, payload: dict[str, Any]) -> MessageEvent:
        message_type = str(payload.get("MsgType", payload.get("msg_type", "text"))).lower()
        event_id = str(payload.get("MsgId") or payload.get("event_id") or _stable_event_id(payload))
        sender_id = str(payload.get("FromUserName") or payload.get("sender_id") or "unknown-sender")
        conversation_id = str(payload.get("ToUserName") or payload.get("conversation_id") or "wechat")
        timestamp = _optional_int(payload.get("CreateTime") or payload.get("timestamp"))

        if message_type == "text":
            text = str(payload.get("Content") or payload.get("text") or "")
            kind = MessageKind.COMMAND if text.strip().startswith("/") else MessageKind.TEXT
            attachments: tuple[Attachment, ...] = ()
        elif message_type == "image":
            text = str(payload.get("Content") or payload.get("text") or "")
            kind = MessageKind.IMAGE
            attachments = (
                Attachment(
                    attachment_id=str(payload.get("MediaId") or payload.get("media_id") or event_id),
                    kind="image",
                    url=_optional_str(payload.get("PicUrl") or payload.get("pic_url")),
                ),
            )
        elif message_type in {"file", "voice", "video"}:
            text = str(payload.get("Content") or payload.get("text") or "")
            kind = MessageKind.FILE
            attachments = (
                Attachment(
                    attachment_id=str(payload.get("MediaId") or payload.get("media_id") or event_id),
                    kind=message_type,
                    name=_optional_str(payload.get("Title") or payload.get("filename")),
                ),
            )
        else:
            text = str(payload.get("Content") or payload.get("text") or "")
            kind = MessageKind.UNKNOWN
            attachments = ()

        return MessageEvent(
            event_id=event_id,
            platform="wechat",
            conversation_id=conversation_id,
            sender_id=sender_id,
            kind=kind,
            text=text,
            timestamp=timestamp,
            reply_to=_optional_str(payload.get("reply_to")),
            attachments=attachments,
            raw=payload,
        )


def _stable_event_id(payload: dict[str, Any]) -> str:
    sender = str(payload.get("FromUserName") or payload.get("sender_id") or "unknown")
    created = str(payload.get("CreateTime") or payload.get("timestamp") or "0")
    content = str(payload.get("Content") or payload.get("text") or "")
    return f"wechat:{sender}:{created}:{abs(hash(content))}"


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
