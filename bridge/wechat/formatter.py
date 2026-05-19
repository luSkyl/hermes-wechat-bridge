"""User-visible WeChat formatting."""

from __future__ import annotations

from bridge.protocol import HermesResponse

ASSISTANT_NAME = "贾维斯"
DIVIDER = "────────────────────────"
TRUNCATION_NOTICE = "…内容较长，我已先保留重点，方便在微信里阅读。"
URGENCY_NOTICE = "…内容较长，我先截到这里；安全相关信息建议优先按现场权威指引处理。"

URGENT_KEYWORDS = (
    "地震",
    "余震",
    "震区",
    "灾区",
    "避险",
    "撤离",
    "报警",
    "急救",
    "危险",
    "紧急",
    "安全",
    "受伤",
    "火灾",
    "洪水",
    "台风",
    "坍塌",
    "泄漏",
    "earthquake",
    "aftershock",
    "emergency",
    "danger",
    "urgent",
    "evacuate",
    "evacuation",
)

DETAIL_MARKERS = ("\n- ", "\n• ", "\n1.", "\n2.", "\n3.", "。", "；", ";")


def format_friendly_reply(response: HermesResponse, max_chars: int = 1800, source_text: str = "") -> str:
    """Format ordinary Hermes replies as a warm WeChat-friendly card."""

    if not response.ok:
        return _fit_to_limit(
            _render_card(
                title="⚠️ 处理遇到问题",
                intro=f"我是「{ASSISTANT_NAME}」，先帮你把问题收住。",
                summary="我这边暂时没能完成处理。",
                detail=_clean(response.error) or "请稍后再试一次。",
                closing="我会尽量保留上下文，方便你继续追问。",
                urgent=True,
            ),
            max_chars,
            urgent=True,
        )

    text = _clean(response.text) or "我已收到，但 Hermes 没有返回可展示内容。"
    urgent = _is_urgent("\n".join((source_text, text)))
    title = "⚠️ 先确认安全" if urgent else "📍 先说结论"
    intro = f"我是「{ASSISTANT_NAME}」，先帮你把重点稳住。" if urgent else f"我是「{ASSISTANT_NAME}」，你的随身执行伙伴 😊"
    closing = "先按安全优先处理；你继续发现场情况，我再帮你一起判断。" if urgent else "你如果想继续，我可以接着帮你拆细节 🌿"
    card = _render_card(title=title, intro=intro, summary=_summary_from(text), detail=_detail_from(text), closing=closing, urgent=urgent)
    return _fit_to_limit(card, max_chars, urgent=urgent)


def format_processing_notice() -> str:
    return _render_card(
        title="🧭 已收到",
        intro=f"我是「{ASSISTANT_NAME}」，你的随身执行伙伴。",
        summary="我正在交给 Hermes 处理。",
        detail="我会尽快把结果整理成好读的回复，方便你直接看重点。",
        closing="稍等一下，我来跟进 ✨",
        urgent=False,
    )


def _render_card(*, title: str, intro: str, summary: str, detail: str, closing: str, urgent: bool) -> str:
    detail_title = "🧭 关键信息" if urgent else "✨ 重点细节"
    action_title = "📌 下一步" if urgent else "🌿 接下来"
    return "\n".join(
        (
            title,
            DIVIDER,
            intro,
            "",
            summary,
            "",
            detail_title,
            detail,
            "",
            action_title,
            closing,
        )
    )


def _summary_from(text: str) -> str:
    paragraphs = _paragraphs(text)
    if not paragraphs:
        return "我已收到你的消息。"
    first = paragraphs[0]
    if len(first) <= 120:
        return first
    return first[:117].rstrip() + "…"


def _detail_from(text: str) -> str:
    paragraphs = _paragraphs(text)
    if not paragraphs:
        return "暂无更多细节。"
    remaining = paragraphs[1:]
    if remaining:
        return "\n".join(_decorate_detail(item) for item in remaining[:4])
    if any(marker in text for marker in DETAIL_MARKERS):
        return text
    return "我已经把核心内容放在上面；如果你需要，我可以继续展开原因、步骤或风险点。"


def _decorate_detail(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith(("- ", "• ", "· ", "1.", "2.", "3.", "4.", "5.")):
        return stripped
    return f"• {stripped}"


def _paragraphs(text: str) -> list[str]:
    return [line.strip() for line in text.replace("\r\n", "\n").split("\n") if line.strip()]


def _fit_to_limit(text: str, max_chars: int, *, urgent: bool) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    suffix = f"\n\n{URGENCY_NOTICE if urgent else TRUNCATION_NOTICE}"
    allowed = max(0, max_chars - len(suffix))
    return text[:allowed].rstrip() + suffix


def _is_urgent(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in URGENT_KEYWORDS)


def _clean(text: object) -> str:
    return str(text or "").strip()
