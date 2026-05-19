import pytest

from bridge.protocol import VerificationError
from bridge.runtime.config import WeChatConfig
from bridge.wechat.adapter import WeChatAdapter
from bridge.wechat.verifier import build_signature, verify_signature


def test_wechat_signature_matches_official_sorting_rule() -> None:
    signature = build_signature(token="dev-token", timestamp="1710000000", nonce="abc")

    assert verify_signature("dev-token", "1710000000", "abc", signature) is True
    assert verify_signature("dev-token", "1710000000", "abc", "bad") is False


def test_adapter_verify_raises_for_invalid_signature() -> None:
    adapter = WeChatAdapter(WeChatConfig(token="dev-token"))

    with pytest.raises(VerificationError):
        adapter.verify(timestamp="1710000000", nonce="abc", signature="bad")


def test_fallback_event_id_is_stable_and_uses_message_fields() -> None:
    adapter = WeChatAdapter(WeChatConfig(token="dev-token"))
    payload = {
        "MsgType": "text",
        "FromUserName": "user-1",
        "ToUserName": "bridge",
        "CreateTime": "1710000000",
        "Content": "hello",
    }

    first = adapter.normalize(dict(payload))
    second = adapter.normalize(dict(payload))
    changed_content = adapter.normalize({**payload, "Content": "hello again"})
    changed_sender = adapter.normalize({**payload, "FromUserName": "user-2"})

    assert first.event_id == second.event_id
    assert first.event_id.startswith("wechat:")
    assert first.event_id != changed_content.event_id
    assert first.event_id != changed_sender.event_id
