from bridge.protocol import DeliveryRequest
from bridge.runtime.config import WeChatConfig
from bridge.wechat.sender import WeChatSender


def test_dry_run_delivery_returns_success_with_request_metadata() -> None:
    sender = WeChatSender(WeChatConfig(token="dev-token", dry_run=True))
    request = DeliveryRequest(conversation_id="bridge", recipient_id="user-1", text="hello")

    result = sender.send(request)

    assert result.ok is True
    assert result.delivery_id == "dry-run:bridge:user-1"
    assert result.metadata["dry_run"] is True
    assert result.metadata["request"]["text"] == "hello"


def test_real_delivery_is_explicitly_not_implemented_in_mvp() -> None:
    sender = WeChatSender(WeChatConfig(token="dev-token", dry_run=False))
    request = DeliveryRequest(conversation_id="bridge", recipient_id="user-1", text="hello")

    result = sender.send(request)

    assert result.ok is False
    assert "not implemented" in str(result.error)
