import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from bridge.hermes import HermesClient
from bridge.protocol import MessageEvent, MessageKind, SessionRef
from bridge.runtime.config import HermesConfig


def test_mock_hermes_contract_returns_stable_shape() -> None:
    client = HermesClient(HermesConfig(mode="mock"))
    event = MessageEvent(
        event_id="contract-1",
        platform="wechat",
        conversation_id="bridge",
        sender_id="user-1",
        kind=MessageKind.TEXT,
        text="hello",
    )
    session = SessionRef.from_message("wechat", "bridge", "user-1")

    response = client.send_message(event, session)

    assert response.ok is True
    assert response.session_id == "wechat:bridge:user-1"
    assert response.text
    assert set(response.to_dict()) == {"text", "session_id", "ok", "error", "metadata"}


def test_http_hermes_contract_accepts_standard_response_shape() -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            assert body["event"]["event_id"] == "contract-2"
            payload = json.dumps(
                {
                    "ok": True,
                    "text": "contract reply",
                    "session_id": body["session"]["session_id"],
                    "error": None,
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_address[1]}/messages"
        client = HermesClient(HermesConfig(mode="http", endpoint=endpoint, timeout_seconds=2))
        event = MessageEvent(
            event_id="contract-2",
            platform="wechat",
            conversation_id="bridge",
            sender_id="user-1",
            kind=MessageKind.TEXT,
            text="hello",
        )
        session = SessionRef.from_message("wechat", "bridge", "user-1")

        response = client.send_message(event, session)

        assert response.ok is True
        assert response.text == "contract reply"
        assert response.session_id == "wechat:bridge:user-1"
    finally:
        server.shutdown()
        server.server_close()
