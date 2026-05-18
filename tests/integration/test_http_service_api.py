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


def test_http_health_status_simulate_and_session_message_contracts() -> None:
    config = load_config("examples/minimal/config.yaml")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(config))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        health = _request_json(f"{base_url}/health")
        status = _request_json(f"{base_url}/status")
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
        session_delivery = _request_json(f"{base_url}/sessions/wechat:bridge:user-1/message", {"text": "manual"})

        assert health["ok"] is True
        assert status["service"] == "hermes-wechat-bridge"
        assert simulate["status"] == "delivered"
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
