# Hermes WeChat Bridge & Distribution Kit

[![CI](https://github.com/luSkyl/hermes-wechat-bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/luSkyl/hermes-wechat-bridge/actions/workflows/ci.yml)
[![CodeQL](https://github.com/luSkyl/hermes-wechat-bridge/actions/workflows/codeql.yml/badge.svg)](https://github.com/luSkyl/hermes-wechat-bridge/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/github/v/release/luSkyl/hermes-wechat-bridge?include_prereleases&label=release)](https://github.com/luSkyl/hermes-wechat-bridge/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Hermes WeChat Bridge is a Windows-first integration kit for running **Hermes Agent + Hermes Web UI + WeChat Bridge** as one reproducible local distribution.

It supports two modes:

- **Bridge-only mode**: install the Python sidecar that normalizes WeChat events, routes them to Hermes, governs delivery, and exposes diagnostics.
- **Full distribution mode**: apply the pinned Hermes Core patch set, replay the Hermes Web UI overlay, install the bridge, and verify the complete runtime.

```text
WeChat User -> Bridge Runtime -> Hermes Agent -> Friendly Reply
                         |-> Delivery Governor / Dedupe / Retry
                         |-> Hermes Web UI Local Overlay
```

## What You Get

- **Clean bridge package** in `bridge/` with callback normalization, signature checks, simulation, service APIs, governed notifications, and Hermes native shims.
- **Full distribution layer** in `distribution/` with a locked component manifest, Hermes Core patches, Hermes Web UI overlay, install/verify/start/rollback scripts, and Windows docs.
- **Upgrade-friendly boundaries**: Core changes are patches, Web UI changes are overlay files, and the bridge remains a normal Python package.
- **Safety by default**: no tokens, WeChat login state, logs, `node_modules`, built runtime bundles, or local secrets are committed.

## Quick Start: Bridge Only

```powershell
git clone https://github.com/luSkyl/hermes-wechat-bridge.git
cd hermes-wechat-bridge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev,yaml]
python -m bridge.cli doctor --config examples/minimal/config.yaml
python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json
python -m bridge.cli serve --config examples/minimal/config.yaml --host 127.0.0.1 --port 8787
```

## Quick Start: Full Distribution

The distribution scripts assemble a complete local Hermes WeChat runtime from pinned sources:

```powershell
git clone https://github.com/luSkyl/hermes-wechat-bridge.git
cd hermes-wechat-bridge
powershell -ExecutionPolicy Bypass -File distribution\scripts\install.ps1 -HermesWorkspaceRoot C:\Hermes\hermes-dist-test
powershell -ExecutionPolicy Bypass -File distribution\scripts\verify.ps1 -HermesWorkspaceRoot C:\Hermes\hermes-dist-test -SkipBridgeHttp
```

For an existing Hermes workspace, run verification first:

```powershell
powershell -ExecutionPolicy Bypass -File distribution\scripts\verify.ps1 -HermesWorkspaceRoot C:\Hermes\hermes -SkipBridgeHttp
```

## Distribution Contents

```text
distribution/
├─ manifest.lock.json                 # pinned Core/Web UI/Bridge versions and hashes
├─ config.example.yaml                 # safe dry-run bridge config
├─ overlays/hermes-web-ui/             # replayable Web UI source overlay
├─ patches/hermes-core/                # Hermes Core source patches
├─ scripts/install.ps1                 # orchestrated install flow
├─ scripts/verify.ps1                  # health and runtime verification
├─ scripts/build-web-ui.ps1            # official Web UI + overlay -> local release
├─ scripts/apply-core-patches.ps1      # patch a clean Hermes Core checkout
├─ scripts/install-bridge.ps1          # install bridge package
├─ scripts/start.ps1                   # start runtime surfaces
├─ scripts/stop.ps1                    # stop local ports
└─ scripts/rollback.ps1                # switch Web UI back to a fallback release
```

Current locked combination:

| Layer | Version / Ref |
|---|---|
| Hermes Core | `v2026.5.16` |
| Hermes Web UI | official `0.5.28` + local overlay -> `0.5.28-local.1` |
| Hermes WeChat Bridge | `0.1.0` / tag `v0.1.0` |

## Architecture

| Layer | Location | Responsibility |
|---|---|---|
| Bridge package | `bridge/` | WeChat callback/service runtime, simulator, governed delivery, diagnostics |
| Core patch set | `distribution/patches/hermes-core/` | Hermes runtime notification/governor integration |
| Web UI overlay | `distribution/overlays/hermes-web-ui/` | Friendly notices, semantic message cards, chat protocol support |
| Installer | `distribution/scripts/` | Build, install, verify, start, stop, rollback |

## Security and Privacy

This repository does not include:

- WeChat login state, cookies, QR sessions, or account data.
- `.env` files, API keys, tokens, or private Hermes home data.
- Runtime logs, user conversations, generated queues, `node_modules`, or built Web UI bundles.

Use `distribution/config.example.yaml` as a template and keep real credentials outside Git.

## Documentation

- `docs/quickstart.md` for bridge-only usage.
- `docs/hermes-native-integration.md` for patchless native shims.
- `distribution/docs/install-windows.md` for full distribution install.
- `distribution/docs/architecture.md` for component boundaries.
- `distribution/docs/upgrade.md` for replaying patches/overlays on new upstream versions.
- `distribution/docs/rollback.md` for recovery paths.

## Release Status

The project has reached the first stable `v0.1.0` GitHub release for the Bridge package and Distribution Kit. PyPI publishing remains gated by repository configuration and trusted publishing setup.
