# WeChat Setup

The exact WeChat setup differs by account type. This project keeps the bridge side explicit and testable.

## Required Values

- Callback URL: public HTTPS endpoint that routes to the bridge.
- Token: long random value shared with WeChat callback verification.
- App ID and app secret: required only for real outbound sending.

## Local Development

Use simulator mode first:

```powershell
python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json
```

Then expose a local callback through your preferred tunneling tool and test signature verification before enabling real delivery.

## Production Checklist

- HTTPS callback configured.
- Token stored outside git.
- Dry-run disabled only after `doctor` passes.
- Logs redacted.
- Retry and dedupe settings tuned for your traffic.
