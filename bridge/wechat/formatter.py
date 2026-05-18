"""User-visible WeChat formatting."""

from __future__ import annotations

from bridge.protocol import HermesResponse


def format_friendly_reply(response: HermesResponse, max_chars: int = 1800) -> str:
    if not response.ok:
        return "我这边暂时没能完成处理，请稍后再试。"
    text = response.text.strip() or "我已收到，但 Hermes 没有返回可展示内容。"
    if len(text) <= max_chars:
        return text
    suffix = "\n\n…内容较长，已为微信展示做截断。"
    return text[: max(0, max_chars - len(suffix))].rstrip() + suffix


def format_processing_notice() -> str:
    return "已收到，我正在交给 Hermes 处理。"
