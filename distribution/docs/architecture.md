# Distribution Architecture

The repository is a single project with four separate responsibilities.

| Area | Path | Purpose |
|---|---|---|
| Bridge package | `bridge/` | Python sidecar for WeChat callbacks, service APIs, delivery governance, and diagnostics. |
| Core patches | `distribution/patches/hermes-core/` | Source patches that replay local Hermes runtime integration on a clean upstream core ref. |
| Web UI overlay | `distribution/overlays/hermes-web-ui/` | Source-only overlay replayed on official Hermes Web UI. |
| Installer | `distribution/scripts/` | PowerShell flows for install, build, verify, start, stop, and rollback. |

The runtime manifest remains the source of truth for a deployed workspace. Built releases and local runtime state are deployment outputs, not repository inputs.

## Do Not Commit

- `runtime/` release bundles.
- `node_modules/` or Web UI `dist/` output.
- `.env`, tokens, cookies, WeChat login sessions, queues, or logs.
- Machine-specific Hermes home state.
