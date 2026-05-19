# Configuration

Configuration is a small YAML-like file. The built-in parser supports simple nested mappings used by the examples. If `PyYAML` is installed, full YAML parsing is used.

## Minimal Configuration

```yaml
bridge:
  name: hermes-wechat-bridge
  environment: local

wechat:
  token: dev-token
  dry_run: true
  app_id: optional-official-account-app-id
  app_secret: optional-official-account-app-secret
  governor_enabled: true
  governor_window_seconds: 60
  governor_initial_capacity: 3
  governor_base_backoff_seconds: 300

hermes:
  mode: mock
  endpoint: http://127.0.0.1:8765/messages

runtime:
  dedupe_ttl_seconds: 300
  dedupe_state_dir: ./.bridge-state/dedupe
  retry_attempts: 2
  retry_backoff_seconds: 0.1
  request_timeout_seconds: 20
  service_api_token: optional-local-admin-token
  allow_unsigned_webhook: false
```

## Secret Handling

- Use `.env` or environment variables for real credentials.
- Keep committed examples in dry-run or mock mode.
- Do not commit real callback tokens, app secrets, chat IDs, or logs.

## Weixin Delivery Governor

`wechat.governor_enabled` should stay enabled for any production-like deployment. The governor protects iLink by counting every outbound send attempt, including failed attempts that never become visible in chat.

- `governor_window_seconds`: size of the learned quota window.
- `governor_initial_capacity`: safe starting budget per window before the bridge learns more.
- `governor_base_backoff_seconds` / `governor_max_backoff_seconds`: protection window after iLink reports rate limiting.
- `governor_max_flush_per_window`: maximum queued messages to release after a successful send.
- `governor_state_dir`: optional file-backed state directory; omit it to use the bridge state directory.

When the governor is open, user-visible content must be a friendly card or local/Web UI status. Do not send a WeChat message just to explain that WeChat is rate limited.

## Official Account Delivery

When `wechat.dry_run` is `false` and both `wechat.app_id` and `wechat.app_secret` are configured, `WeChatSender` uses the official custom-message text API by default. Keep dry-run enabled until the callback signature check, token acquisition, and a small manual delivery smoke test all pass.

## Runtime Notification Adapters

Use `BridgeNotifier` for direct `send_message_tool`-style notifications, `CronDeliveryNotifier` for scheduled-task alerts, and `GuardianDeliveryNotifier` for watchdog incidents. These adapters always render friendly cards before calling `WeChatSender`, so raw stack traces, `ret=-2`, and transport errors are not sent to chat.

Run `python -m bridge.cli notify --config <config> --target <chat-id> --text <message>` to send or queue a governed friendly-card notification, and `python -m bridge.cli flush --config <config> --target <chat-id>` to release queued cards in a later window.

For patchless Hermes runtime wiring, use the Hermes Native Integration Kit: `python -m bridge.cli install-hermes-native --hermes-home <path> --config <config> --target <chat-id>`.

## Production Notes

- Set `wechat.dry_run` to `false` only after webhook verification works.
- Keep `runtime.allow_unsigned_webhook` set to `false` in production. It is only for tightly controlled local callback experiments; `/simulate` remains the preferred unsigned test path.
- Set `runtime.dedupe_state_dir` to a writable runtime directory when running multiple workers or when callback retries must survive process restarts.
- Use HTTPS for callbacks.
- Keep Hermes endpoint private when possible.
- Set `runtime.service_api_token` before binding the callback server to a non-loopback host.
