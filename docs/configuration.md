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

## Production Notes

- Set `wechat.dry_run` to `false` only after webhook verification works.
- Use HTTPS for callbacks.
- Keep Hermes endpoint private when possible.
- Set `runtime.service_api_token` before binding the callback server to a non-loopback host.
