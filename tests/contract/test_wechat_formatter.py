"""Formatter contract tests."""

from __future__ import annotations

from bridge.hermes import HermesClient
from bridge.protocol import HermesResponse
from bridge.runtime.friendly_card import contains_divider, divider_for
from bridge.runtime.config import BridgeConfig, HermesConfig, RuntimeConfig, WeChatConfig
from bridge.runtime.router import GatewayRouter
from bridge.wechat import WeChatAdapter, WeChatSender
from bridge.wechat.formatter import format_friendly_reply, format_processing_notice, looks_like_friendly_reply


def _config(tmp_path) -> BridgeConfig:
    return BridgeConfig(
        name="test",
        environment="test",
        hermes=HermesConfig(mode="mock"),
        wechat=WeChatConfig(token="test-token", dry_run=True, governor_state_dir=str(tmp_path)),
        runtime=RuntimeConfig(),
    )


def test_friendly_card_divider_adapts_to_message_length() -> None:
    short = divider_for("短消息")
    medium = divider_for("中等消息" * 30)
    long = divider_for("很长的消息" * 100)

    assert len(short) == 12
    assert len(short) < len(medium) < len(long) <= 24


def test_friendly_reply_uses_card_layout_for_normal_text() -> None:
    response = HermesResponse(text="先做结论\n然后补充原因\n|---|---|\n最后给下一步", session_id="s-1")

    text = format_friendly_reply(response)

    assert text.startswith("📍 先说结论")
    assert "📍 先说结论" in text
    assert "|---|---|" not in text
    assert "✨ 重点细节" in text
    assert "然后补充原因" in text
    assert "最后给下一步" in text
    assert "🌿 接下来" in text
    assert "先做结论" in text
    assert looks_like_friendly_reply(text)
    assert contains_divider(text)


def test_friendly_reply_does_not_wrap_existing_card() -> None:
    card = format_friendly_reply(HermesResponse(text="先做结论\n然后补充原因", session_id="s-1"))

    assert format_friendly_reply(HermesResponse(text=card, session_id="s-1")) == card


def test_friendly_reply_truncates_long_text() -> None:
    response = HermesResponse(text="这是一段很长的说明。" * 300, session_id="s-1")

    text = format_friendly_reply(response, max_chars=200)

    assert len(text) <= 200
    assert "…内容较长" in text


def test_friendly_reply_avoids_smiley_style_for_urgent_context() -> None:
    response = HermesResponse(text="请尽快撤离，附近有地震和余震风险", session_id="s-1")

    text = format_friendly_reply(response, source_text="现在在地震区，请优先给安全建议")

    assert text.startswith("⚠️ 先确认安全")
    assert "😊" not in text
    assert "😄" not in text
    assert "安全优先" in text or "现场权威指引" in text


def test_processing_notice_uses_friendly_card() -> None:
    text = format_processing_notice()

    assert text.startswith("🧭 已收到")
    assert "📌 当前情况" in text
    assert "稍等一下" in text


def test_router_formats_reply_with_source_context(tmp_path) -> None:
    config = _config(tmp_path)
    sender = WeChatSender(config.wechat)
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=sender)
    adapter = WeChatAdapter(config.wechat)
    message = adapter.normalize(
        {
            "MsgId": "formatter-card-1",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "Content": "现在在地震区，请给我安全建议",
        }
    )

    result = router.handle_event(message)

    assert result.status == "delivered"
    assert result.reply_text is not None
    assert result.reply_text.startswith("⚠️ 先确认安全")
    assert "😊" not in result.reply_text


