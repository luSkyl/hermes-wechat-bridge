from __future__ import annotations

from pathlib import Path

from bridge.wechat.governor import (
    HALF_OPEN,
    OPEN,
    WeixinDeliveryGovernor,
    WeixinDeliveryGovernorConfig,
    is_rate_limited_result,
)


def make_governor(tmp_path: Path, **overrides: object) -> WeixinDeliveryGovernor:
    values = {
        "state_dir": tmp_path,
        "window_seconds": 60,
        "initial_capacity": 2,
        "min_capacity": 1,
        "max_capacity": 5,
        "base_backoff_seconds": 60,
        "max_backoff_seconds": 60,
        "jitter_seconds": 0,
    }
    values.update(overrides)
    config = WeixinDeliveryGovernorConfig(**values)
    return WeixinDeliveryGovernor(config)


def test_attempts_count_against_window_capacity(tmp_path: Path) -> None:
    governor = make_governor(tmp_path)

    first = governor.admit_or_queue("one", target_id="user-1", now=1000)
    second = governor.admit_or_queue("two", target_id="user-1", now=1001)
    third = governor.admit_or_queue("three", target_id="user-1", now=1002)

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.queued is True
    assert third.reason == "queued_quota_exhausted"
    assert third.queue_size == 1


def test_rate_limit_result_opens_breaker_and_queues_next_message(tmp_path: Path) -> None:
    governor = make_governor(tmp_path)

    assert governor.admit_or_queue("one", target_id="user-1", now=1000).allowed is True
    status = governor.record_result(success=False, error_text="iLink sendmessage rate limited: ret=-2", now=1001)
    decision = governor.admit_or_queue("two", target_id="user-1", now=1002)

    assert status["status"] == OPEN
    assert decision.allowed is False
    assert decision.queued is True
    assert decision.reason == "queued_rate_limited"
    assert decision.next_available_at == 1061
    assert is_rate_limited_result({"error": "errcode=-2"}) is True


def test_half_open_allows_one_canary_only(tmp_path: Path) -> None:
    governor = make_governor(tmp_path)

    assert governor.admit_or_queue("one", target_id="user-1", now=1000).allowed is True
    governor.record_result(success=False, error_text="rate limited ret=-2", now=1001)

    canary = governor.admit_or_queue("canary", target_id="user-1", now=1062)
    second = governor.admit_or_queue("second", target_id="user-1", now=1063)

    assert canary.allowed is True
    assert canary.status == HALF_OPEN
    assert second.allowed is False
    assert second.queued is True
    assert second.reason == "queued_rate_limited"


def test_priority_queue_and_stale_expiration(tmp_path: Path) -> None:
    governor = make_governor(tmp_path, initial_capacity=1, low_priority_ttl_seconds=5)

    assert governor.admit_or_queue("slot", target_id="user-1", now=1000).allowed is True
    low = governor.admit_or_queue("low", target_id="user-1", priority="low", now=1001)
    high = governor.admit_or_queue("high", target_id="user-1", priority="high", now=1002)

    assert low.queued is True
    assert high.queued is True
    plan = governor.flush_plan(target_id="user-1", limit=5, now=1062)

    assert [item.message for item in plan] == ["high"]


def test_friendly_card_hides_raw_rate_limit_markers(tmp_path: Path) -> None:
    governor = make_governor(tmp_path)

    assert governor.admit_or_queue("one", target_id="user-1", now=1000).allowed is True
    governor.record_result(success=False, error_text="RuntimeError: ret=-2", now=1001)
    decision = governor.admit_or_queue("two", target_id="user-1", now=1002)

    assert decision.friendly_text is not None
    assert "【状态】" in decision.friendly_text
    assert "【下一步】" in decision.friendly_text
    assert "ret=-2" not in decision.friendly_text
    assert "RuntimeError" not in decision.friendly_text
    assert "Traceback" not in decision.friendly_text
    assert decision.friendly_text.startswith("◇ 微信发送已进入保护队列")
