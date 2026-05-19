import json
import urllib.error
import urllib.request
from dataclasses import replace
from http.server import ThreadingHTTPServer
from threading import Thread

import pytest

from bridge.protocol import ConfigurationError
from bridge.runtime.config import load_config
from bridge.server import _build_handler, serve
from bridge.wechat.verifier import build_signature


def test_http_health_status_simulate_and_notification_contracts() -> None:
    config = load_config("examples/minimal/config.yaml")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(config))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        health = _request_json(f"{base_url}/health")
        status = _request_json(f"{base_url}/status")
        delivery_status = _request_json(f"{base_url}/delivery/status")
        simulate = _request_json(
            f"{base_url}/simulate",
            {
                "MsgId": "http-sim-1",
                "MsgType": "text",
                "FromUserName": "user-1",
                "ToUserName": "bridge",
                "Content": "hello",
            },
        )
        notification = _request_json(f"{base_url}/notify", {"target_id": "wxid_home", "text": "hello"})
        flush = _request_json(f"{base_url}/flush", {"target_id": "wxid_home", "limit": 3})
        session_delivery = _request_json(f"{base_url}/sessions/wechat:bridge:user-1/message", {"text": "manual"})

        assert health["ok"] is True
        assert status["service"] == "hermes-wechat-bridge"
        assert status["contracts"]["delivery_status"] == "/delivery/status"
        assert status["contracts"]["notify"] == "/notify"
        assert status["contracts"]["flush"] == "/flush"
        assert delivery_status["enabled"] is True
        assert simulate["status"] == "delivered"
        assert notification["ok"] is True
        assert "【状态】" in notification["metadata"]["request"]["text"]
        assert flush["ok"] is True
        assert session_delivery["ok"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_service_api_requires_token_when_configured() -> None:
    config = load_config("examples/minimal/config.yaml")
    config = replace(config, runtime=replace(config.runtime, service_api_token="secret-token"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(config))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with pytest.raises(urllib.error.HTTPError) as error_info:
            _request_json(f"{base_url}/status")
        assert error_info.value.code == 401
        authorized = _request_json(f"{base_url}/status", headers={"X-Bridge-Token": "secret-token"})
        assert authorized["service"] == "hermes-wechat-bridge"
    finally:
        server.shutdown()
        server.server_close()


def test_non_loopback_serve_requires_service_api_token() -> None:
    with pytest.raises(ConfigurationError):
        serve("examples/minimal/config.yaml", host="0.0.0.0", port=0)


def test_wechat_callback_post_requires_signature_fields() -> None:
    config = load_config("examples/minimal/config.yaml")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(config))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with pytest.raises(urllib.error.HTTPError) as error_info:
            _request_json(
                base_url,
                {
                    "MsgId": "unsigned-callback",
                    "MsgType": "text",
                    "FromUserName": "user-1",
                    "ToUserName": "bridge",
                    "Content": "hello",
                },
            )
        assert error_info.value.code == 403
    finally:
        server.shutdown()
        server.server_close()


def test_wechat_callback_post_accepts_valid_signature() -> None:
    config = load_config("examples/minimal/config.yaml")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(config))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    timestamp = "1710000000"
    nonce = "abc"
    signature = build_signature(config.wechat.token, timestamp, nonce)
    base_url = f"http://127.0.0.1:{server.server_address[1]}?signature={signature}&timestamp={timestamp}&nonce={nonce}"
    try:
        result = _request_text(
            base_url,
            json.dumps(
                {
                    "MsgId": "signed-callback",
                    "MsgType": "text",
                    "FromUserName": "user-1",
                    "ToUserName": "bridge",
                    "Content": "hello",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        assert result.startswith("<xml>")
        assert "Hermes mock reply" in result
    finally:
        server.shutdown()
        server.server_close()


def _request_json(
    url: str,
    payload: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    request_headers = headers or {}
    if payload is None:
        request = urllib.request.Request(url, headers=request_headers, method="GET")
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **request_headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=2) as response:
        return json.loads(response.read().decode("utf-8"))


def _request_text(url: str, payload: bytes, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, data=payload, headers=headers or {}, method="POST")
    with urllib.request.urlopen(request, timeout=2) as response:
        return response.read().decode("utf-8")
