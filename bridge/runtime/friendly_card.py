"""Friendly user-visible notification cards.

Every operator-facing notification should flow through this module before it is
sent to WeChat. The renderer uses a plain-text shape so it works with personal
WeChat, official-account bridges, dry-run logs, and tests without a rich-card API.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

RAW_ERROR_PATTERNS = (
    re.compile(r"Traceback \(most recent call last\):.*", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bTraceback\b", re.IGNORECASE),
    re.compile(r"\bRuntimeError\b", re.IGNORECASE),
    re.compile(r"ret=-?\d+", re.IGNORECASE),
    re.compile(r"errcode=-?\d+", re.IGNORECASE),
    re.compile(r"https?://\S+", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9_\-]{24,}"),
)

_SEVERITY_ICONS = {
    "info": "💬",
    "success": "🌿",
    "warning": "⏳",
    "error": "🛟",
    "critical": "🚨",
}


@dataclass(frozen=True)
class FriendlySection:
    """A section in a friendly notification card."""

    title: str
    body: str | Iterable[str]

    def render(self) -> str:
        body_text = _join_body(self.body)
        return f"【{sanitize_user_visible(self.title)}】\n{body_text}".strip()


@dataclass(frozen=True)
class FriendlyCard:
    """Plain-text friendly card contract for all notifications."""

    title: str
    summary: str
    severity: str = "info"
    sections: tuple[FriendlySection, ...] = ()
    actions: tuple[str, ...] = ()
    footer: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        icon = _SEVERITY_ICONS.get(self.severity, _SEVERITY_ICONS["info"])
        parts = [f"{icon} {sanitize_user_visible(self.title)}", "", "【状态】", sanitize_user_visible(self.summary)]
        for section in self.sections:
            rendered = section.render()
            if rendered:
                parts.extend(["", rendered])
        if self.actions:
            parts.extend(["", "【下一步】", _join_body(self.actions)])
        if self.footer:
            parts.extend(["", sanitize_user_visible(self.footer)])
        return "\n".join(parts).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "severity": self.severity,
            "sections": [section.render() for section in self.sections],
            "actions": list(self.actions),
            "footer": self.footer,
            "metadata": self.metadata,
            "text": self.render(),
        }


def friendly_card(
    *,
    title: str,
    summary: str,
    severity: str = "info",
    sections: Iterable[tuple[str, str | Iterable[str]]] | None = None,
    actions: Iterable[str] | None = None,
    footer: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Render a friendly card in the shared user-visible template."""

    return FriendlyCard(
        title=title,
        summary=summary,
        severity=severity,
        sections=tuple(FriendlySection(title=item[0], body=item[1]) for item in (sections or ())),
        actions=tuple(actions or ()),
        footer=footer,
        metadata=dict(metadata or {}),
    ).render()


def ensure_friendly_card(
    text: str,
    *,
    title: str = "通知已接收",
    severity: str = "info",
    action: str = "无需操作，我会继续跟进。",
) -> str:
    """Return a card even when callers pass a raw notification string."""

    clean = sanitize_user_visible(text)
    if looks_like_friendly_card(clean):
        return clean
    return friendly_card(
        title=title,
        summary="有一条需要你知晓的状态更新。",
        severity=severity,
        sections=(("内容", clean),),
        actions=(action,),
    )


def delivery_deferred_card(*, reason: str, queue_size: int | None = None, next_available_at: float | None = None) -> str:
    """Card shown in logs/UI when Weixin delivery is queued instead of sent now."""

    queue_text = "正在排队"
    if queue_size is not None:
        queue_text = f"正在排队，当前约 {queue_size} 条待发送"
    return friendly_card(
        title="微信通知已暂存",
        summary="为避免继续触发 iLink 限流，这条通知没有立即发送到微信。",
        severity="warning",
        sections=(
            ("原因", sanitize_user_visible(reason)),
            ("队列", queue_text),
            ("预计", _format_next_available(next_available_at)),
        ),
        actions=("我会在下一个可发送窗口自动补发。", "如果是紧急事项，请改用本地控制台或 Web UI 查看。"),
    )


def delivery_failed_card(*, reason: str) -> str:
    """Card for non-rate-limit delivery failures."""

    return friendly_card(
        title="微信通知发送失败",
        summary="通知没有成功送达，我已经保留可排查的安全摘要。",
        severity="error",
        sections=(("失败原因", sanitize_user_visible(reason)),),
        actions=("请检查发送适配器配置和网络连通性。",),
    )


def cron_failure_card(*, job_name: str, reason: str, next_run: str | None = None) -> str:
    """Friendly card for scheduled-job failures."""

    sections: list[tuple[str, str]] = [("任务", job_name), ("原因", sanitize_user_visible(reason))]
    if next_run:
        sections.append(("下次计划", next_run))
    return friendly_card(
        title="定时任务需要关注",
        summary="有一个定时任务没有按预期完成。",
        severity="warning",
        sections=sections,
        actions=("我会继续观察并在恢复后给出恢复卡片。",),
    )


def cron_recovery_card(*, job_name: str, detail: str = "任务已恢复正常。") -> str:
    """Friendly card for scheduled-job recovery."""

    return friendly_card(
        title="定时任务已恢复",
        summary="之前异常的定时任务已经重新跑通。",
        severity="success",
        sections=(("任务", job_name), ("结果", sanitize_user_visible(detail))),
        actions=("无需操作。",),
    )


def guardian_incident_card(*, name: str, state: str, reason: str, action: str | None = None) -> str:
    """Friendly card for Guardian-style incident notifications."""

    return friendly_card(
        title="守护进程发现异常",
        summary="有一个被守护的链路需要关注。",
        severity="critical" if state.lower() in {"down", "failed", "critical"} else "warning",
        sections=(("对象", name), ("状态", state), ("原因", sanitize_user_visible(reason))),
        actions=(action or "我会继续检测，恢复后发送恢复卡片。",),
    )


def guardian_recovery_card(*, name: str, detail: str = "链路已恢复。") -> str:
    """Friendly card for Guardian-style recovery notifications."""

    return friendly_card(
        title="守护进程已恢复",
        summary="之前异常的链路已经恢复。",
        severity="success",
        sections=(("对象", name), ("结果", sanitize_user_visible(detail))),
        actions=("无需操作。",),
    )


def looks_like_friendly_card(text: str) -> bool:
    return "【状态】" in text and any(text.startswith(icon) for icon in _SEVERITY_ICONS.values())


def sanitize_user_visible(text: Any) -> str:
    value = str(text or "").strip()
    if not value:
        return "未提供详情。"
    for pattern in RAW_ERROR_PATTERNS:
        value = pattern.sub("[已隐藏技术细节]", value)
    return value[:1800]


def _join_body(body: str | Iterable[str]) -> str:
    if isinstance(body, str):
        return sanitize_user_visible(body)
    return "\n".join(f"- {sanitize_user_visible(item)}" for item in body)


def _format_next_available(next_available_at: float | None) -> str:
    if not next_available_at:
        return "等待治理器打开下一个发送窗口。"
    timestamp = datetime.fromtimestamp(float(next_available_at), tz=UTC)
    return f"约 {timestamp.isoformat(timespec='seconds')} 后可重试。"


