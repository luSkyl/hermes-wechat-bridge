"""In-process stable service API helpers used by tests and future UI adapters."""

from __future__ import annotations

from bridge.hermes import HermesClient
from bridge.protocol import DeliveryRequest, DeliveryResult, SessionRef
from bridge.runtime.config import BridgeConfig
from bridge.runtime.diagnostics import run_diagnostics
from bridge.runtime.router import GatewayRouter, RouteResult
from bridge.wechat import WeChatAdapter, WeChatSender


class BridgeService:
    """Small facade for stable bridge operations."""

    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self.adapter = WeChatAdapter(config.wechat)
        self.sender = WeChatSender(config.wechat)
        self.router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=self.sender)

    def health(self) -> dict[str, object]:
        return run_diagnostics(self.config).to_dict()

    def status(self) -> dict[str, object]:
        return {
            "ok": True,
            "service": "hermes-wechat-bridge",
            "environment": self.config.environment,
            "hermes_mode": self.config.hermes.mode,
            "wechat_dry_run": self.config.wechat.dry_run,
        }

    def simulate(self, payload: dict[str, object]) -> RouteResult:
        return self.router.handle_event(self.adapter.normalize(payload))

    def send_session_message(self, session_id: str, text: str) -> DeliveryResult:
        session = self._parse_session_id(session_id)
        request = DeliveryRequest(
            conversation_id=session.conversation_id,
            recipient_id=session.sender_id,
            text=text[: self.config.wechat.max_reply_chars],
            metadata={"session_id": session.session_id, "source": "service-api"},
        )
        return self.sender.send(request)

    @staticmethod
    def _parse_session_id(session_id: str) -> SessionRef:
        parts = session_id.split(":", 2)
        if len(parts) != 3:
            raise ValueError("session id must use platform:conversation:sender")
        platform, conversation_id, sender_id = parts
        return SessionRef(session_id=session_id, platform=platform, conversation_id=conversation_id, sender_id=sender_id)
