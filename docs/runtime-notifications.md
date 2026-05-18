# Runtime Notifications

The bridge ships the reusable notification layer that local Hermes deployments use around Weixin delivery governance. A downstream runtime does not need to copy private Cron, Guardian, or `send_message_tool` code to get the same user-visible behavior.

## Contract

Every message that is meant to notify an operator must be rendered through the friendly-card contract before it reaches WeChat:

- Use `bridge.runtime.notifier.BridgeNotifier` for direct notifications and `send_message_tool`-style sends.
- Use `bridge.runtime.cron.CronDeliveryNotifier` for scheduled-job failure and recovery cards.
- Use `bridge.runtime.guardian.GuardianDeliveryNotifier` for watchdog/guardian incident and recovery cards.
- Use `WeChatSender.flush_queued()` or `BridgeNotifier.flush_queued()` to drain queued notifications in later send windows.

The sender admits every outbound attempt through `WeixinDeliveryGovernor`. If iLink returns `ret=-2`, `errcode=-2`, or another rate-limit marker, the attempt is counted, the circuit opens, and the original friendly card is queued for a later flush instead of sending a second WeChat message explaining the rate limit.

## Direct Notification

```python
from bridge.runtime.config import WeChatConfig
from bridge.runtime.notifier import BridgeNotifier
from bridge.wechat.sender import WeChatSender

sender = WeChatSender(WeChatConfig(token="wechat-token", dry_run=True))
notifier = BridgeNotifier(sender)

result = notifier.notify_text(
    target_id="wxid_home",
    title="上游模型已恢复",
    text="模型恢复后需要重新执行定时任务。",
    priority="high",
)
```

## Cron Adapter

```python
from bridge.runtime.cron import CronDeliveryNotifier, CronJobNotice

cron = CronDeliveryNotifier(notifier)
cron.failure(CronJobNotice(
    target_id="wxid_home",
    job_name="morning-report",
    reason="采集脚本没有按时完成",
    next_run="09:00",
))
cron.recovery(CronJobNotice(
    target_id="wxid_home",
    job_name="morning-report",
    reason="脚本已重新跑通",
))
```

## Guardian Adapter

```python
from bridge.runtime.guardian import GuardianDeliveryNotifier, GuardianIncident

guardian = GuardianDeliveryNotifier(notifier)
guardian.incident(GuardianIncident(
    target_id="wxid_home",
    name="upstream-model",
    state="failed",
    reason="模型健康检查失败",
))
guardian.recovery(GuardianIncident(
    target_id="wxid_home",
    name="upstream-model",
    state="recovered",
    reason="健康检查恢复",
))
```

## Flush Queued Notifications

```python
results = notifier.flush_queued(target_id="wxid_home", limit=3)
```

Run this from your scheduler after a successful send, after a backoff window, or from a local/Web UI button. The governor limits flush volume per window so queued background notices do not re-trigger iLink rate limiting.
