"""Official Account outbound text transport."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any

from bridge.protocol import DeliveryRequest, DeliveryResult
from bridge.runtime.config import WeChatConfig

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
CUSTOM_SEND_URL = "https://api.weixin.qq.com/cgi-bin/message/custom/send"


class OfficialAccountTextTransport:
    """Send text messages through the WeChat Official Account custom message API."""

    def __init__(self, config: WeChatConfig, timeout_seconds: float = 10.0) -> None:
        if not config.app_id or not config.app_secret:
            raise ValueError("wechat.app_id and wechat.app_secret are required for official account delivery")
        self.config = config
        self.timeout_seconds = timeout_seconds
        self._access_token: str | None = None
        self._access_token_expires_at = 0.0

    def __call__(self, request: DeliveryRequest) -> DeliveryResult:
        try:
            access_token = self._get_access_token()
            payload = json.dumps(
                {
                    "touser": request.recipient_id,
                    "msgtype": "text",
                    "text": {"content": request.text},
                },
                ensure_ascii=False,
            ).encode("utf-8")
            url = f"{CUSTOM_SEND_URL}?access_token={urllib.parse.quote(access_token)}"
            http_request = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            response = _read_json(http_request, timeout_seconds=self.timeout_seconds)
        except (TimeoutError, urllib.error.URLError, ValueError) as error:
            return DeliveryResult(ok=False, error=str(error), metadata={"transport": "wechat-official"})

        errcode = int(response.get("errcode") or 0)
        errmsg = str(response.get("errmsg") or "ok")
        if errcode == 0:
            return DeliveryResult(
                ok=True,
                delivery_id=f"wechat-official:{uuid.uuid4().hex[:16]}",
                metadata={"transport": "wechat-official", "errcode": errcode, "errmsg": errmsg},
            )
        return DeliveryResult(
            ok=False,
            error=f"WeChat API errcode={errcode}: {errmsg}",
            metadata={"transport": "wechat-official", "errcode": errcode, "errmsg": errmsg},
        )

    def _get_access_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._access_token_expires_at:
            return self._access_token
        query = urllib.parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": self.config.app_id,
                "secret": self.config.app_secret,
            }
        )
        response = _read_json(f"{TOKEN_URL}?{query}", timeout_seconds=self.timeout_seconds)
        token = str(response.get("access_token") or "").strip()
        if not token:
            errcode = response.get("errcode", "unknown")
            errmsg = response.get("errmsg", "missing access_token")
            raise ValueError(f"WeChat token API errcode={errcode}: {errmsg}")
        expires_in = int(response.get("expires_in") or 7200)
        self._access_token = token
        self._access_token_expires_at = now + max(60, expires_in - 60)
        return token


def _read_json(request: str | urllib.request.Request, *, timeout_seconds: float) -> dict[str, Any]:
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body or "{}")
    if not isinstance(parsed, dict):
        raise ValueError("WeChat API response must be a JSON object")
    return parsed
