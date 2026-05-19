# Hermes Web UI Overlay

This overlay replays the Web UI enhancements required by the Hermes WeChat distribution on top of the official `hermes-web-ui` `v0.5.28` baseline.

It contains only source changes:

- `patches/0001-local-enhancements.patch` for tracked upstream files.
- `files/` for new files that do not exist in upstream.
- `scripts/` for applying, verifying, building, and smoke-testing the overlay.

It intentionally does not include built `dist/` output, `node_modules`, runtime state, tokens, or machine-specific paths.
