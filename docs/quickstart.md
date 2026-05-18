# Quickstart

This guide runs the bridge in mock Hermes mode. You do not need real WeChat credentials for the first smoke test.

## 1. Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

## 2. Check Configuration

```powershell
python -m bridge.cli doctor --config examples/minimal/config.yaml
```

The demo config uses `mock` Hermes mode and a local WeChat dry-run sender.

## 3. Simulate a WeChat Message

```powershell
python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json
```

You should see a normalized inbound event, a Hermes response, and a friendly outbound message.

## 4. Start a Local Callback Server

```powershell
python -m bridge.cli serve --config examples/minimal/config.yaml --host 127.0.0.1 --port 8787
```

The server supports WeChat GET verification and POST callback handling for local testing. Put it behind HTTPS before using it with real WeChat callbacks.

## 5. Switch to Real Hermes

Update `examples/minimal/config.yaml` or copy it to a private file:

```yaml
hermes:
  mode: http
  endpoint: http://127.0.0.1:8765/messages
```

## 6. Switch to Real WeChat

Follow [WeChat Setup](wechat-setup.md), configure HTTPS callback routing, then set real secrets through environment variables or an ignored private config file.

## Success Criteria

- `doctor` passes.
- `simulate` returns a friendly reply.
- Duplicate events are acknowledged without reprocessing.
- Hermes failures return a safe, user-friendly failure message.
