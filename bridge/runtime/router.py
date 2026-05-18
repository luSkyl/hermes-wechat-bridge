"""Bridge router connecting WeChat events to Hermes and delivery."""

from __future__ import annotations

from dataclasses import dataclass

from bridge.hermes import HermesClient
from bridge.protocol import DeliveryRequest, DeliveryResult, MessageEvent, SessionRef
from bridge.runtime.config import BridgeConfig
from bridge.runtime.dedupe import DedupeStore
from bridge.runtime.retry import retry_call
from bridge.wechat.formatter import format_friendly_reply
from bridge.wechat.sender import WeChatSender


@dataclass(frozen=True)
class RouteResult:
    status: str
    event_id: str
    session_id: str | None
    reply_text: str | None
    delivery: DeliveryResult | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "event_id": self.event_id,
            "session_id": self.session_id,
            "reply_text": self.reply_text,
            "delivery": self.delivery.to_dict() if self.delivery else None,
        }


class GatewayRouter:
    """Route normalized events through Hermes and back to WeChat."""

    def __init__(self, config: BridgeConfig, hermes: HermesClient, sender: WeChatSender) -> None:
        self.config = config
        self.hermes = hermes
        self.sender = sender
        self.dedupe = DedupeStore(ttl_seconds=config.runtime.dedupe_ttl_seconds)

    def handle_event(self, event: MessageEvent) -> RouteResult:
        if self.dedupe.seen(event.event_id):
            return RouteResult(
                status="duplicate",
                event_id=event.event_id,
                session_id=None,
                reply_text=None,
                delivery=None,
            )

        session = SessionRef.from_message(event.platform, event.conversation_id, event.sender_id)
        hermes_response = self.hermes.send_message(event, session)
        reply_text = format_friendly_reply(hermes_response, max_chars=self.config.wechat.max_reply_chars)
        delivery_request = DeliveryRequest(
            conversation_id=event.conversation_id,
            recipient_id=event.sender_id,
            text=reply_text,
            reply_to=event.reply_to,
            metadata={"event_id": event.event_id, "session_id": session.session_id},
        )

        delivery_result, attempts = retry_call(
            lambda: self.sender.send(delivery_request),
            attempts=self.config.runtime.retry_attempts,
            backoff_seconds=self.config.runtime.retry_backoff_seconds,
        )
        if delivery_result.attempts != attempts:
            delivery_result = DeliveryResult(
                ok=delivery_result.ok,
                delivery_id=delivery_result.delivery_id,
                error=delivery_result.error,
                attempts=attempts,
                metadata=delivery_result.metadata,
            )
        return RouteResult(
            status="delivered" if delivery_result.ok else "delivery_failed",
            event_id=event.event_id,
            session_id=session.session_id,
            reply_text=reply_text,
            delivery=delivery_result,
        )
