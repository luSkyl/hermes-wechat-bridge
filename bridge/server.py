"""Minimal WeChat callback server for local and small deployments."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from bridge.hermes import HermesClient
from bridge.protocol import (
    ConfigurationError,
    DeliveryRequest,
    SessionRef,
    VerificationError,
)
from bridge.runtime.config import BridgeConfig, load_config
from bridge.runtime.diagnostics import run_diagnostics
from bridge.runtime.router import GatewayRouter
from bridge.wechat import WeChatAdapter, WeChatSender
from bridge.wechat.verifier import verify_signature
from bridge.wechat.xml import parse_wechat_xml, render_text_reply


def serve(config_path: str, host: str = "127.0.0.1", port: int = 8787) -> None:
    config = load_config(config_path)
    if not _is_loopback_host(host) and not config.runtime.service_api_token:
        raise ConfigurationError("runtime.service_api_token is required when serving on a non-loopback host")
    handler = _build_handler(config)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Hermes WeChat Bridge listening on http://{host}:{port}")
    server.serve_forever()


def _build_handler(config: BridgeConfig) -> type[BaseHTTPRequestHandler]:
    adapter = WeChatAdapter(config.wechat)
    sender = WeChatSender(config.wechat)
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=sender)

    class WeChatCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            parsed_url = urlparse(self.path)
            if parsed_url.path == "/health":
                if not self._authorize_service_api():
                    return
                result = run_diagnostics(config)
                self._write_json(200 if result.ok else 503, result.to_dict())
                return
            if parsed_url.path == "/status":
                if not self._authorize_service_api():
                    return
                self._write_json(200, _status_payload(config))
                return

            query = parse_qs(parsed_url.query)
            signature = _first(query, "signature")
            timestamp = _first(query, "timestamp")
            nonce = _first(query, "nonce")
            echostr = _first(query, "echostr")
            if signature and timestamp and nonce and verify_signature(config.wechat.token, timestamp, nonce, signature):
                self._write(200, echostr or "ok", content_type="text/plain")
                return
            self._write(403, "invalid signature", content_type="text/plain")

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            parsed_url = urlparse(self.path)
            try:
                if parsed_url.path == "/simulate":
                    if not self._authorize_service_api():
                        return
                    payload = self._read_json_body()
                    result = router.handle_event(adapter.normalize(payload))
                    self._write_json(200, result.to_dict())
                    return
                if parsed_url.path.startswith("/sessions/") and parsed_url.path.endswith("/message"):
                    if not self._authorize_service_api():
                        return
                    session_id = unquote(parsed_url.path.removeprefix("/sessions/").removesuffix("/message").strip("/"))
                    payload = self._read_json_body()
                    result = _send_session_message(config, sender, session_id, payload)
                    self._write_json(200 if result.ok else 502, result.to_dict())
                    return
            except Exception as error:  # noqa: BLE001 - service API returns safe error
                self._write_json(400, {"ok": False, "error": str(error)})
                return

            query = parse_qs(parsed_url.query)
            signature = _first(query, "signature")
            timestamp = _first(query, "timestamp")
            nonce = _first(query, "nonce")
            try:
                if signature and timestamp and nonce:
                    adapter.verify(timestamp=timestamp, nonce=nonce, signature=signature)
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                payload = _parse_body(body, self.headers.get("Content-Type", ""))
                result = router.handle_event(adapter.normalize(payload))
                if result.reply_text and payload.get("FromUserName") and payload.get("ToUserName"):
                    reply_xml = render_text_reply(
                        to_user=str(payload["FromUserName"]),
                        from_user=str(payload["ToUserName"]),
                        content=result.reply_text,
                    )
                    self._write(200, reply_xml, content_type="application/xml")
                    return
                self._write(200, json.dumps(result.to_dict(), ensure_ascii=False), content_type="application/json")
            except VerificationError:
                self._write(403, "invalid signature", content_type="text/plain")
            except Exception as error:  # noqa: BLE001 - callback server returns safe error
                self._write_json(500, {"ok": False, "error": str(error)})

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - inherited API
            return

        def _write(self, status: int, body: str, content_type: str) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _write_json(self, status: int, payload: dict[str, object]) -> None:
            self._write(status, json.dumps(payload, ensure_ascii=False), content_type="application/json")

        def _read_json_body(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            loaded = json.loads(body or "{}")
            if not isinstance(loaded, dict):
                raise ValueError("JSON body must be an object")
            return loaded

        def _authorize_service_api(self) -> bool:
            expected = config.runtime.service_api_token
            if not expected:
                return True
            authorization = self.headers.get("Authorization", "")
            bridge_token = self.headers.get("X-Bridge-Token", "")
            if authorization == f"Bearer {expected}" or bridge_token == expected:
                return True
            self._write_json(401, {"ok": False, "error": "service API authentication required"})
            return False

    return WeChatCallbackHandler


def _first(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    if not values:
        return None
    return values[0]


def _parse_body(body: str, content_type: str) -> dict[str, object]:
    if "json" in content_type.lower():
        loaded = json.loads(body)
        if not isinstance(loaded, dict):
            raise ValueError("JSON body must be an object")
        return loaded
    return parse_wechat_xml(body)


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower()
    return normalized in {"127.0.0.1", "localhost", "::1"}


def _status_payload(config: BridgeConfig) -> dict[str, object]:
    return {
        "ok": True,
        "service": "hermes-wechat-bridge",
        "environment": config.environment,
        "hermes_mode": config.hermes.mode,
        "wechat_dry_run": config.wechat.dry_run,
        "contracts": {
            "health": "/health",
            "status": "/status",
            "simulate": "/simulate",
            "session_message": "/sessions/{id}/message",
        },
    }


def _send_session_message(
    config: BridgeConfig,
    sender: WeChatSender,
    session_id: str,
    payload: dict[str, object],
):
    session = _parse_session_id(session_id)
    text = str(payload.get("text") or "").strip()
    if not text:
        raise ValueError("text is required")
    request = DeliveryRequest(
        conversation_id=session.conversation_id,
        recipient_id=session.sender_id,
        text=text[: config.wechat.max_reply_chars],
        metadata={"session_id": session.session_id, "source": "service-api"},
    )
    return sender.send(request)


def _parse_session_id(session_id: str) -> SessionRef:
    parts = session_id.split(":", 2)
    if len(parts) != 3:
        raise ValueError("session id must use platform:conversation:sender")
    platform, conversation_id, sender_id = parts
    return SessionRef(session_id=session_id, platform=platform, conversation_id=conversation_id, sender_id=sender_id)
