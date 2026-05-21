from __future__ import annotations

from pathlib import Path

from bridge.protocol import DeliveryResult
from bridge.runtime.config import WeChatConfig
from bridge.runtime.cron import CronDeliveryNotifier, CronJobNotice
from bridge.runtime.friendly_card import cron_failure_card, guardian_incident_card
from bridge.runtime.guardian import GuardianDeliveryNotifier, GuardianIncident
from bridge.runtime.notifier import BridgeNotifier
from bridge.wechat.sender import WeChatSender


def _sender(tmp_path: Path, **overrides: object) -> WeChatSender:
    values = {
        "token": "test-token",
        "dry_run": True,
        "governor_state_dir": str(tmp_path),
        "governor_initial_capacity": 1,
        "governor_min_capacity": 1,
        "governor_max_capacity": 3,
    }
    values.update(overrides)
    return WeChatSender(WeChatConfig(**values))


def test_notify_text_wraps_raw_message_into_friendly_card(tmp_path: Path) -> None:
    notifier = BridgeNotifier(_sender(tmp_path))

    result = notifier.notify_text(target_id="wxid_home", text="Traceback ret=-2 abcdefghijklmnopqrstuvwxyz")

    request_text = result.metadata["request"]["text"]
    assert result.ok is True
    assert "📌 当前情况" in request_text
    assert "ret=-2" not in request_text
    assert "Traceback" not in request_text
    assert "📌 当前情况" in result.metadata["user_message"]


def test_notify_text_hides_provider_auth_errors(tmp_path: Path) -> None:
    notifier = BridgeNotifier(_sender(tmp_path))

    result = notifier.notify_text(
        target_id="wxid_home",
        text="❌ Non-retryable error (HTTP 401): Error code: 401 - {'code': 'INVALID_API_KEY'}; trying fallback...",
    )

    request_text = result.metadata["request"]["text"]
    assert result.ok is True
    assert "📌 当前情况" in request_text
    assert "HTTP 401" not in request_text
    assert "INVALID_API_KEY" not in request_text
    assert "trying fallback" not in request_text
    assert "Non-retryable" not in request_text


def test_notifier_queues_when_governor_capacity_is_exhausted(tmp_path: Path) -> None:
    notifier = BridgeNotifier(_sender(tmp_path))

    first = notifier.notify_text(target_id="wxid_home", text="first")
    second = notifier.notify_text(target_id="wxid_home", text="second")

    assert first.ok is True
    assert second.ok is True
    assert second.metadata["queued"] is True
    assert second.attempts == 0
    assert "📌 当前情况" in second.metadata["user_message"]


def test_transport_rate_limit_counts_attempt_and_queues_original_message(tmp_path: Path) -> None:
    def rate_limited_transport(_request):
        return DeliveryResult(ok=False, error="iLink sendmessage rate limited ret=-2", attempts=1)

    sender = WeChatSender(
        WeChatConfig(token="test-token", dry_run=False, governor_state_dir=str(tmp_path), governor_initial_capacity=2),
        transport=rate_limited_transport,
    )
    notifier = BridgeNotifier(sender)

    result = notifier.notify_text(target_id="wxid_home", text="important", priority="high")

    assert result.ok is True
    assert result.metadata["queued"] is True
    assert result.attempts == 1
    assert sender.governor.status()["status"] == "OPEN"
    assert "ret=-2" not in result.metadata["user_message"]


def test_cron_and_guardian_notifications_use_friendly_templates(tmp_path: Path) -> None:
    notifier = BridgeNotifier(_sender(tmp_path, governor_initial_capacity=3))
    cron = CronDeliveryNotifier(notifier)
    guardian = GuardianDeliveryNotifier(notifier)

    cron_result = cron.failure(
        CronJobNotice(target_id="wxid_home", job_name="morning-report", reason="RuntimeError ret=-2", next_run="09:00")
    )
    guardian_result = guardian.incident(
        GuardianIncident(target_id="wxid_home", name="upstream-model", state="failed", reason="HTTP 500 traceback")
    )

    assert "📌 当前情况" in cron_result.metadata["request"]["text"]
    assert "ret=-2" not in cron_result.metadata["request"]["text"]
    assert "📌 当前情况" in guardian_result.metadata["request"]["text"]
    assert "Traceback" not in guardian_result.metadata["request"]["text"]


def test_template_helpers_are_friendly_cards() -> None:
    cron_text = cron_failure_card(job_name="sync", reason="ret=-2 raw error")
    guardian_text = guardian_incident_card(name="model", state="failed", reason="Traceback ret=-2")

    assert "📌 当前情况" in cron_text
    assert "📌 当前情况" in guardian_text
    assert "ret=-2" not in cron_text
    assert "Traceback" not in guardian_text
