# Compatibility Matrix

This matrix defines the contracts that make Hermes, Hermes Web UI, and hermes-wechat-bridge independently upgradeable.

## Supported Contracts

| Boundary | Contract | Owner | Compatibility Gate |
|---|---|---|---|
| Bridge -> Hermes | `HermesClient.send_message(event, session)` | Bridge | `tests/integration/test_hermes_contract.py` |
| Hermes -> Bridge | HTTP/CLI response shape: `ok`, `text`, `session_id`, `error` | Hermes + Bridge | Hermes contract fixture tests |
| Web UI -> Bridge | `GET /health`, `GET /status`, `POST /simulate`, `POST /sessions/{id}/message` | Bridge | `tests/integration/test_bridge_service_api.py` |
| WeChat -> Bridge | signature verification + message normalization | Bridge | WeChat contract tests |

## Version Policy

| Component | Upgrade Rule | Expected Fix Location |
|---|---|---|
| Hermes | Upgrade upstream first, then run Hermes contract tests. | Prefer `bridge/hermes/client.py`; only add tiny Hermes hook if needed. |
| Hermes Web UI | Upgrade upstream first, then run Bridge service API tests. | Prefer Web UI adapter/view changes; bridge runtime should not change for UI-only upgrades. |
| hermes-wechat-bridge | Upgrade independently, then run full bridge tests. | Bridge repo only. |

## Stable Hermes Response Shape

```json
{
  "ok": true,
  "text": "reply shown to the user",
  "session_id": "wechat:conversation:user",
  "error": null
}
```

## Stable Bridge Service API

- `GET /health`: liveness and diagnostic checks.
- `GET /status`: safe bridge runtime metadata.
- `POST /simulate`: local event replay for UI and operators.
- `POST /sessions/{id}/message`: optional direct session message for integration tests and controlled tools.

The in-process equivalent lives in `bridge.runtime.service.BridgeService` for tests and future adapters that do not need HTTP.

See `docs/service-api.md` for endpoint examples and Web UI ownership rules.

## Breaking Change Rule

Breaking changes require:

1. A migration note.
2. A compatibility window or explicit version bump.
3. Updated contract tests.
4. Rollback instructions.
