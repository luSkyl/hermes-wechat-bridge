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
  governor_enabled: true
  governor_window_seconds: 60
  governor_initial_capacity: 3
  governor_base_backoff_seconds: 300

hermes:
  mode: mock
  endpoint: http://127.0.0.1:8765/messages

runtime:
  dedupe_ttl_seconds: 300
  retry_attempts: 2
  retry_backoff_seconds: 0.1
  request_timeout_seconds: 20
  service_api_token: optional-local-admin-token
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

## Production Notes

- Set `wechat.dry_run` to `false` only after webhook verification works.
- Use HTTPS for callbacks.
- Keep Hermes endpoint private when possible.
- Set `runtime.service_api_token` before binding the callback server to a non-loopback host.
