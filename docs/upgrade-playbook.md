# Upgrade Playbook

Use this playbook whenever Hermes, Hermes Web UI, or hermes-wechat-bridge changes.

## Upgrade Hermes

1. Update Hermes from upstream.
2. Do not merge WeChat-specific runtime changes into Hermes.
3. Start Hermes with its stable API or CLI hook.
4. Run bridge Hermes contract tests.
5. Fix compatibility in `bridge/hermes/client.py` unless Hermes truly lacks a stable hook.

## Upgrade Hermes Web UI

1. Update Hermes Web UI from upstream.
2. Keep bridge features optional and read-only.
3. Validate Web UI can call bridge `GET /health` and `GET /status`.
4. Optionally validate `POST /simulate` in a non-production or dry-run environment.
5. Do not move WeChat callback, delivery, retry, or session logic into Web UI.

## Upgrade hermes-wechat-bridge

1. Run unit and integration tests.
2. Run `doctor` and `simulate` against example config.
3. Validate callback server service APIs.
4. Confirm no real secrets or runtime state are included.
5. Publish or deploy bridge independently.

## Rollback

- Bridge failure: roll back only bridge version or enable dry-run.
- Hermes failure: roll back Hermes while keeping bridge config unchanged.
- Web UI failure: roll back Web UI; bridge message delivery should continue.
