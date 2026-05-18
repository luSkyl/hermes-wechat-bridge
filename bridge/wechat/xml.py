"""Minimal WeChat XML parsing and rendering helpers."""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from html import escape


def parse_wechat_xml(text: str) -> dict[str, str]:
    root = ET.fromstring(text)
    payload: dict[str, str] = {}
    for child in root:
        payload[child.tag] = child.text or ""
    return payload


def render_text_reply(to_user: str, from_user: str, content: str) -> str:
    created_at = int(time.time())
    return (
        "<xml>"
        f"<ToUserName><![CDATA[{to_user}]]></ToUserName>"
        f"<FromUserName><![CDATA[{from_user}]]></FromUserName>"
        f"<CreateTime>{created_at}</CreateTime>"
        "<MsgType><![CDATA[text]]></MsgType>"
        f"<Content><![CDATA[{_safe_cdata(content)}]]></Content>"
        "</xml>"
    )


def _safe_cdata(content: str) -> str:
    return escape(content.replace("]]>", "]]&gt;"), quote=False)
