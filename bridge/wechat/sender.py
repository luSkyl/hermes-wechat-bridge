"""WeChat outbound sender."""

from __future__ import annotations

from bridge.protocol import DeliveryRequest, DeliveryResult
from bridge.runtime.config import WeChatConfig
from bridge.wechat.governor import WeixinDeliveryGovernor, WeixinDeliveryGovernorConfig


class WeChatSender:
    """Send replies to WeChat or emit dry-run delivery results."""

    def __init__(self, config: WeChatConfig) -> None:
        self.config = config
        self.governor = WeixinDeliveryGovernor(
            WeixinDeliveryGovernorConfig(
                enabled=config.governor_enabled,
                state_dir=config.governor_state_dir,
                window_seconds=config.governor_window_seconds,
                initial_capacity=config.governor_initial_capacity,
                min_capacity=config.governor_min_capacity,
                max_capacity=config.governor_max_capacity,
                max_flush_per_window=config.governor_max_flush_per_window,
                queue_max_size=config.governor_queue_max_size,
                base_backoff_seconds=config.governor_base_backoff_seconds,
                max_backoff_seconds=config.governor_max_backoff_seconds,
                low_priority_ttl_seconds=config.governor_low_priority_ttl_seconds,
                default_ttl_seconds=config.governor_default_ttl_seconds,
                high_priority_ttl_seconds=config.governor_high_priority_ttl_seconds,
                critical_ttl_seconds=config.governor_critical_ttl_seconds,
            )
        )

    def send(self, request: DeliveryRequest) -> DeliveryResult:
        decision = self.governor.admit_or_queue(
            request.text,
            target_id=request.recipient_id,
            priority=str(request.metadata.get("priority") or "normal"),
            source=str(request.metadata.get("source") or "bridge"),
            metadata={"conversation_id": request.conversation_id, **request.metadata},
        )
        if not decision.allowed:
            return DeliveryResult(
                ok=True,
                delivery_id=decision.delivery_id,
                attempts=0,
                metadata={"governed": True, "queued": decision.queued, **decision.to_dict()},
            )
        if self.config.dry_run:
            self.governor.record_result(success=True)
            return DeliveryResult(
                ok=True,
                delivery_id=f"dry-run:{request.conversation_id}:{request.recipient_id}",
                metadata={"dry_run": True, "governed": True, "request": request.to_dict(), "governor": decision.to_dict()},
            )
        self.governor.record_result(success=False, error_text="real delivery adapter missing")
        return DeliveryResult(
            ok=False,
            error="Real WeChat outbound delivery is not implemented yet. Keep dry_run enabled or add a sender adapter.",
            metadata={"dry_run": False, "governed": True, "governor": decision.to_dict()},
        )
