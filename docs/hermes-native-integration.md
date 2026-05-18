# Hermes Native Integration Kit

Hermes WeChat Bridge ships a patchless integration kit so open-source users can get the same governed Weixin notification behavior without forking Hermes core.

## What It Provides

- `send_message_tool`-style governed notifications via `bridge.integrations.hermes_native.send_message_tool_shim`.
- Cron failure/recovery notifications via `CronDeliveryNotifier`.
- Guardian/watchdog incident/recovery notifications via `GuardianDeliveryNotifier`.
- Friendly-card rendering for every user-visible notification.
- File-backed Weixin Delivery Governor for attempt budgeting, circuit breaking, queueing, and flush.
- Patchless generated wrappers under `<hermes-home>/.hermes-wechat-bridge/shims`.

## Install From a Clean Clone

```powershell
git clone https://github.com/luSkyl/hermes-wechat-bridge.git
cd hermes-wechat-bridge
python -m pip install -e .[yaml]
python -m bridge.cli doctor --config examples/hermes-native/config.yaml
python -m bridge.cli install-hermes-native --hermes-home ./.demo-hermes-home --config examples/hermes-native/config.yaml --target wxid_home --force
python -m bridge.cli verify-hermes-native --hermes-home ./.demo-hermes-home
```

The installer writes only generated shim files and an `integration.json` manifest. It does not copy or patch a Hermes runtime checkout.

## Direct Notification

```powershell
python -m bridge.cli notify --config examples/hermes-native/config.yaml --target wxid_home --title "上游模型已恢复" --text "模型恢复后需要重新执行定时任务。" --priority high
```

## Queue Status and Flush

```powershell
python -m bridge.cli queue-status --config examples/hermes-native/config.yaml
python -m bridge.cli flush --config examples/hermes-native/config.yaml --target wxid_home --limit 3
```

## Generated Shim Files

After installation, `<hermes-home>/.hermes-wechat-bridge/shims` contains:

- `send_message_tool_bridge.py`
- `cron_bridge.py`
- `guardian_bridge.py`

Your Hermes runtime, Cron runner, or watchdog can import those wrappers from its own hook layer. The wrappers call the package APIs; they do not contain private local paths.

## Python API

```python
from bridge.integrations.hermes_native import send_message, notify_cron_failure, notify_guardian_incident

send_message(
    config_path="examples/hermes-native/config.yaml",
    target_id="wxid_home",
    title="上游模型已恢复",
    text="模型恢复后需要重新执行定时任务。",
    priority="high",
)

notify_cron_failure(
    config_path="examples/hermes-native/config.yaml",
    target_id="wxid_home",
    job_name="morning-report",
    reason="采集脚本没有按时完成",
)

notify_guardian_incident(
    config_path="examples/hermes-native/config.yaml",
    target_id="wxid_home",
    name="upstream-model",
    state="failed",
    reason="健康检查失败",
)
```

## Non-Negotiable Delivery Contract

Every notification path must pass through this sequence:

1. Render a friendly card.
2. Ask `WeixinDeliveryGovernor` for an attempt budget.
3. Send only if admitted.
4. Queue when quota/circuit blocks delivery.
5. Return local/Web UI friendly status instead of sending a second WeChat message about WeChat rate limiting.

User-visible messages must not contain raw `Traceback`, `ret=-2`, `errcode=-2`, tokens, secrets, or raw transport stack traces.

## Acceptance Smoke

```powershell
python -m py_compile bridge/**/*.py
python -m ruff check bridge tests
python -m pytest tests -q
python examples/hermes-native/send-message-demo.py
```
