"""Hermes client abstraction."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from bridge.protocol import HermesResponse, MessageEvent, SessionRef
from bridge.runtime.config import HermesConfig


class HermesClient:
    """Send normalized messages to Hermes Agent."""

    def __init__(self, config: HermesConfig) -> None:
        self.config = config

    def send_message(self, event: MessageEvent, session: SessionRef) -> HermesResponse:
        if self.config.mode == "mock":
            return HermesResponse(
                text=f"Hermes mock reply: {event.prompt_text()}",
                session_id=session.session_id,
                metadata={"mode": "mock"},
            )
        return self._send_http(event, session)

    def _send_http(self, event: MessageEvent, session: SessionRef) -> HermesResponse:
        if not self.config.endpoint:
            return HermesResponse(text="", session_id=session.session_id, ok=False, error="Missing Hermes endpoint")
        payload = json.dumps({"event": event.to_dict(), "session": session.__dict__}).encode("utf-8")
        request = urllib.request.Request(
            self.config.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as error:
            return HermesResponse(text="", session_id=session.session_id, ok=False, error=str(error))

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return HermesResponse(text=body, session_id=session.session_id)
        return HermesResponse(
            text=str(parsed.get("text") or parsed.get("reply") or ""),
            session_id=str(parsed.get("session_id") or session.session_id),
            ok=bool(parsed.get("ok", True)),
            error=parsed.get("error"),
            metadata={"mode": "http", "status": "parsed"},
        )
