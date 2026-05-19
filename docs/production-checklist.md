# Production Checklist

## Before Launch

- [ ] `doctor` passes with the production config.
- [ ] Real secrets are stored outside git.
- [ ] HTTPS callback is configured.
- [ ] WeChat signature verification is enabled.
- [ ] Unsigned webhook fallback is disabled (`runtime.allow_unsigned_webhook: false`).
- [ ] Hermes endpoint is reachable and protected.
- [ ] Dedupe TTL, persistent state directory, and retry settings are tuned.
- [ ] Delivery-governor state directory is outside git, access-restricted, backed up if needed, and retention-limited.
- [ ] Logs are redacted and retention-limited.
- [ ] Friendly fallback messages are reviewed.

## Smoke Tests

- [ ] Text message receives a reply.
- [ ] Duplicate webhook does not produce a duplicate reply.
- [ ] Hermes downtime returns a friendly failure message.
- [ ] Delivery failure is retried and recorded.
- [ ] Overlong response is safely formatted.

## Rollback

- Re-enable dry-run mode.
- Disable public callback routing.
- Rotate exposed credentials if needed.
- Restore the last known-good config.
