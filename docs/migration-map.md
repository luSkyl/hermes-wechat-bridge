# Migration Map

This map tracks how existing Hermes or Hermes Web UI capabilities should move into the independent bridge without changing user-visible behavior.

## Capability Mapping

| Existing Capability | Target Owner | Target Module | Migration Notes |
|---|---|---|---|
| WeChat callback verification | hermes-wechat-bridge | `bridge/wechat/verifier.py`, `bridge/server.py` | Keep token handling outside git. |
| WeChat inbound parsing | hermes-wechat-bridge | `bridge/wechat/adapter.py`, `bridge/wechat/xml.py` | Normalize into `MessageEvent`. |
| WeChat outbound formatting | hermes-wechat-bridge | `bridge/wechat/formatter.py`, `bridge/wechat/sender.py` | Keep user-facing failures friendly and safe. |
| Message dedupe | hermes-wechat-bridge | `bridge/runtime/dedupe.py` | Dedupe by event ID before invoking Hermes. |
| Retry/backoff | hermes-wechat-bridge | `bridge/runtime/retry.py`, `bridge/runtime/router.py` | Retries belong to delivery/runtime, not Hermes core. |
| Session mapping | hermes-wechat-bridge | `bridge/protocol/session.py` | Use stable session IDs across upgrades. |
| Hermes execution | Hermes | Stable API or CLI hook | Do not move Agent runtime into bridge. |
| Web UI bridge status | Hermes Web UI | Optional read-only panel | Consume bridge service APIs only. |
| Local logs/state | none | none | Do not migrate. |

## Migration Order

1. Freeze behavior in simulator fixtures and tests.
2. Migrate protocol model and fixtures.
3. Migrate WeChat adapter and callback handling.
4. Migrate reliability behavior: dedupe, retry, friendly fallback.
5. Migrate diagnostics and operator docs.
6. Disable duplicate Hermes/Hermes Web UI implementations.
7. Run Hermes upgrade smoke, Web UI upgrade smoke, and bridge full tests.

## Done Criteria

- The bridge can process a WeChat message without importing Hermes internals.
- Hermes can upgrade with only Hermes contract tests required.
- Hermes Web UI can upgrade without owning WeChat runtime logic.
- Bridge can be published as a clean open-source repository.
