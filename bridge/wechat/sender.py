"""WeChat outbound sender."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bridge.protocol import DeliveryRequest, DeliveryResult
from bridge.runtime.config import WeChatConfig
from bridge.runtime.friendly_card import delivery_deferred_card, delivery_failed_card, friendly_card
from bridge.wechat.governor import WeixinDeliveryGovernor, WeixinDeliveryGovernorConfig, is_rate_limited_result

SendTransport = Callable[[DeliveryRequest], DeliveryResult]


class WeChatSender:
    """Send replies to WeChat or emit dry-run delivery results."""

    def __init__(self, config: WeChatConfig, transport: SendTransport | None = None) -> None:
        self.config = config
        self.transport = transport
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
            return self._queued_result(request, decision.to_dict(), attempts=0)
        if self.config.dry_run:
            self.governor.record_result(success=True)
            return DeliveryResult(
                ok=True,
                delivery_id=f"dry-run:{request.conversation_id}:{request.recipient_id}",
                metadata={
                    "dry_run": True,
                    "governed": True,
                    "request": request.to_dict(),
                    "governor": decision.to_dict(),
                    "user_message": friendly_card(
                        title="通知已模拟发送",
                        summary="这是一条 dry-run 结果，真实发送已交给上游 transport。",
                        severity="info",
                    ),
                },
            )
        return self._attempt_transport(request, decision.to_dict())

    def flush_queued(self, *, target_id: str, limit: int | None = None) -> list[DeliveryResult]:
        results: list[DeliveryResult] = []
        for queued in self.governor.flush_plan(target_id=target_id, limit=limit):
            request = DeliveryRequest(
                conversation_id=str(queued.metadata.get("conversation_id") or "queued"),
                recipient_id=target_id,
                text=queued.message,
                reply_to=str(queued.metadata.get("reply_to") or "") or None,
                metadata={
                    **queued.metadata,
                    "priority": queued.priority,
                    "source": queued.source,
                    "delivery_id": queued.delivery_id,
                    "flushed": True,
                    "governed": True,
                },
            )
            results.append(self._attempt_transport(request, {"queued_delivery": queued.to_dict(), "flush": True}, attempts=queued.attempts))
        return results

    def _attempt_transport(self, request: DeliveryRequest, governor_data: dict[str, Any], attempts: int = 1) -> DeliveryResult:
        if self.config.dry_run:
            self.governor.record_result(success=True)
            return DeliveryResult(
                ok=True,
                delivery_id=f"dry-run:{request.conversation_id}:{request.recipient_id}",
                attempts=attempts,
                metadata={
                    "dry_run": True,
                    "governed": True,
                    "request": request.to_dict(),
                    "governor": governor_data,
                    "user_message": friendly_card(
                        title="通知已模拟发送",
                        summary="这是一条 dry-run 结果，真实发送已交给上游 transport。",
                        severity="info",
                    ),
                },
            )

        if self.transport is None:
            self.governor.record_result(success=False, error_text="real delivery adapter missing")
            return DeliveryResult(
                ok=False,
                error="Real WeChat outbound delivery is not implemented yet. Keep dry_run enabled or provide a transport.",
                attempts=attempts,
                metadata={
                    "dry_run": False,
                    "governed": True,
                    "governor": governor_data,
                    "user_message": delivery_failed_card(reason="real delivery adapter missing"),
                },
            )

        try:
            result = self.transport(request)
        except Exception as exc:  # noqa: BLE001 - transport boundary
            error_text = str(exc)
            self.governor.record_result(success=False, error_text=error_text)
            if is_rate_limited_result(error_text):
                queued_decision = self.governor.queue_delivery(
                    request.text,
                    target_id=request.recipient_id,
                    priority=str(request.metadata.get("priority") or "normal"),
                    source=str(request.metadata.get("source") or "bridge"),
                    metadata={"conversation_id": request.conversation_id, **request.metadata},
                )
                return self._queued_result(request, queued_decision.to_dict(), error_text=error_text, attempts=attempts)
            return DeliveryResult(
                ok=False,
                error=error_text,
                attempts=attempts,
                metadata={
                    "governed": True,
                    "governor": governor_data,
                    "user_message": delivery_failed_card(reason=error_text),
                },
            )

        self.governor.record_result(success=result.ok, error_text=result.error)
        if result.ok:
            metadata = {"governed": True, "governor": governor_data, **result.metadata}
            return DeliveryResult(
                ok=True,
                delivery_id=result.delivery_id,
                attempts=result.attempts,
                metadata=metadata,
            )

        error_text = str(result.error or "delivery_failed")
        if is_rate_limited_result(error_text):
            queued_decision = self.governor.queue_delivery(
                request.text,
                target_id=request.recipient_id,
                priority=str(request.metadata.get("priority") or "normal"),
                source=str(request.metadata.get("source") or "bridge"),
                metadata={"conversation_id": request.conversation_id, **request.metadata},
            )
            return self._queued_result(request, queued_decision.to_dict(), error_text=error_text, attempts=result.attempts)

        return DeliveryResult(
            ok=False,
            delivery_id=result.delivery_id,
            error=error_text,
            attempts=result.attempts,
            metadata={
                "governed": True,
                "governor": governor_data,
                "user_message": delivery_failed_card(reason=error_text),
                **result.metadata,
            },
        )

    def _queued_result(
        self,
        request: DeliveryRequest,
        governor_data: dict[str, Any],
        *,
        error_text: str | None = None,
        attempts: int = 0,
    ) -> DeliveryResult:
        return DeliveryResult(
            ok=True,
            delivery_id=str(governor_data.get("delivery_id") or f"queued:{request.conversation_id}:{request.recipient_id}"),
            attempts=attempts,
            metadata={
                "queued": True,
                "governed": True,
                "request": request.to_dict(),
                "governor": governor_data,
                "error": error_text,
                "user_message": delivery_deferred_card(
                    reason=str(governor_data.get("reason") or error_text or "queued"),
                    queue_size=governor_data.get("queue_size"),
                ),
            },
        )
