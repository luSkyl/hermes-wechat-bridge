# Full Distribution Install on Windows

This guide installs the complete Hermes WeChat distribution from this repository.

## Prerequisites

- Windows PowerShell 5.1 or PowerShell 7.
- Git available on `PATH`.
- Python 3.11+ available on `PATH`.
- Node.js and npm available on `PATH`.
- Network access to clone Hermes Core and Hermes Web UI baselines.

## Install

Use a fresh workspace when validating reproducibility:

```powershell
git clone https://github.com/luSkyl/hermes-wechat-bridge.git
cd hermes-wechat-bridge
powershell -ExecutionPolicy Bypass -File distribution\scripts\install.ps1 -HermesWorkspaceRoot C:\Hermes\hermes-dist-test
```

The installer performs these steps:

1. Clones Hermes Core at the locked ref from `distribution/manifest.lock.json`.
2. Applies `distribution/patches/hermes-core/*.patch`.
3. Clones Hermes Web UI at the locked ref.
4. Applies `distribution/overlays/hermes-web-ui`.
5. Runs focused tests and a production build unless skipped.
6. Installs the bridge package from this repository.
7. Writes a starter runtime manifest when the workspace does not already have one.
8. Starts and verifies the local runtime unless skipped.

## Verify an Existing Workspace

```powershell
powershell -ExecutionPolicy Bypass -File distribution\scripts\verify.ps1 -HermesWorkspaceRoot C:\Hermes\hermes -SkipBridgeHttp
```

Use `-SkipBridgeHttp` when the bridge service is not currently running as an HTTP server.

## Configuration

Copy `distribution/config.example.yaml` and edit only the copy. Do not commit credentials, tokens, local queues, logs, or WeChat state.
