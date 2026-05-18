"""WeChat outbound sender."""

from __future__ import annotations

from bridge.protocol import DeliveryRequest, DeliveryResult
from bridge.runtime.config import WeChatConfig


class WeChatSender:
    """Send replies to WeChat or emit dry-run delivery results."""

    def __init__(self, config: WeChatConfig) -> None:
        self.config = config

    def send(self, request: DeliveryRequest) -> DeliveryResult:
        if self.config.dry_run:
            return DeliveryResult(
                ok=True,
                delivery_id=f"dry-run:{request.conversation_id}:{request.recipient_id}",
                metadata={"dry_run": True, "request": request.to_dict()},
            )
        return DeliveryResult(
            ok=False,
            error="Real WeChat outbound delivery is not implemented in the MVP. Keep dry_run enabled or add a sender adapter.",
            metadata={"dry_run": False},
        )
