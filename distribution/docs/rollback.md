# Rollback Guide

## Web UI Rollback

Use the rollback script to switch the runtime manifest back to an official fallback release:

```powershell
powershell -ExecutionPolicy Bypass -File distribution\scripts\rollback.ps1 -HermesWorkspaceRoot C:\Hermes\hermes -FallbackWebUiRelease 0.5.28
```

If you saved a manifest backup, prefer restoring it:

```powershell
powershell -ExecutionPolicy Bypass -File distribution\scripts\rollback.ps1 -HermesWorkspaceRoot C:\Hermes\hermes -BackupManifest C:\Hermes\backups\active-runtime.before.json
```

## Core Rollback

Keep the previous clean core release until a patched release has passed observation. Restore the runtime manifest to the previous core root and restart gateway/Web UI.

## Bridge Rollback

Install a prior tag with pip or check out the prior Git tag, then restart the bridge service.
