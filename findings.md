# Findings: Hermes WeChat Bridge

## Repository Context

- The existing workspace contains several repositories and runtime artifacts; the new open-source deliverable must live in a clean `hermes-wechat-bridge` directory.
- Existing Hermes gateway evidence shows mature concepts: platform adapters, config loading, runner lifecycle, message governance, and platform extension documentation.
- The requested product is not a direct code dump. It is a new golden-path project for Hermes to WeChat.

## Design Decisions

- Use a single repository with clear modules instead of multiple repos for the MVP.
- Focus on one path: Hermes Agent -> Bridge Runtime -> WeChat Adapter -> friendly WeChat reply.
- Keep dependencies minimal and pure Python standard library where possible, plus `pytest` and `PyYAML` for tests/config convenience.
- Provide a deterministic simulator so users can validate the bridge without real WeChat credentials.

## Non-Goals

- No multi-platform gateway in v1.
- No Web UI in v1.
- No copying private configs, logs, tokens, channel IDs, or historical task evidence.
- No full replacement for Hermes Agent.
