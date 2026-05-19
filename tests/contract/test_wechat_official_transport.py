import json
from io import BytesIO

import bridge.wechat.official as official
from bridge.protocol import DeliveryRequest
from bridge.runtime.config import WeChatConfig
from bridge.wechat import OfficialAccountTextTransport, WeChatSender


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_official_account_transport_fetches_token_and_sends_text(monkeypatch) -> None:
    calls: list[object] = []

    def fake_urlopen(request, timeout):
        calls.append(request)
        if isinstance(request, str):
            assert "grant_type=client_credential" in request
            return _Response({"access_token": "access-token", "expires_in": 7200})
        body = json.loads(BytesIO(request.data).read().decode("utf-8"))
        assert "access_token=access-token" in request.full_url
        assert body == {"touser": "user-1", "msgtype": "text", "text": {"content": "hello"}}
        return _Response({"errcode": 0, "errmsg": "ok"})

    monkeypatch.setattr(official.urllib.request, "urlopen", fake_urlopen)
    transport = OfficialAccountTextTransport(
        WeChatConfig(token="dev-token", dry_run=False, app_id="app-id", app_secret="app-secret")
    )

    result = transport(DeliveryRequest(conversation_id="bridge", recipient_id="user-1", text="hello"))

    assert result.ok is True
    assert result.metadata["transport"] == "wechat-official"
    assert len(calls) == 2


def test_sender_uses_official_transport_when_credentials_exist() -> None:
    sender = WeChatSender(WeChatConfig(token="dev-token", dry_run=False, app_id="app-id", app_secret="app-secret"))

    assert isinstance(sender.transport, OfficialAccountTextTransport)
