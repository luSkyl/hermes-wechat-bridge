"""send_message_tool-compatible governed notification shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bridge.runtime.config import load_config
from bridge.runtime.notifier import BridgeNotifier
from bridge.runtime.service import BridgeService
from bridge.wechat import WeChatSender


def send_message(
    *,
    config_path: str | Path,
    target_id: str,
    text: str,
    title: str = "通知已接收",
    priority: str = "normal",
    source: str = "send_message_tool",
    metadata: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Send or queue a friendly-card notification.

    This is the portable open-source equivalent of a Hermes ``send_message_tool``
    notification path. The returned payload is JSON-serializable and treats a
    governed queued result as successful-but-deferred.
    """

    config = load_config(config_path)
    notifier = BridgeNotifier(WeChatSender(config.wechat))
    result = notifier.notify_text(
        target_id=target_id,
        text=text,
        title=title,
        source=source,
        priority=priority,
        metadata=metadata,
    )
    return result.to_dict()


def flush_queued(*, config_path: str | Path, target_id: str, limit: int | None = None) -> dict[str, object]:
    """Flush queued governed notifications for a target."""

    config = load_config(config_path)
    notifier = BridgeNotifier(WeChatSender(config.wechat))
    results = notifier.flush_queued(target_id=target_id, limit=limit)
    return {"ok": all(item.ok for item in results), "count": len(results), "results": [item.to_dict() for item in results]}


def queue_status(*, config_path: str | Path) -> dict[str, object]:
    """Return safe governor state for local dashboards/Web UI."""

    service = BridgeService(load_config(config_path))
    return service.delivery_status()
