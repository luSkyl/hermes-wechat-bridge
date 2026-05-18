"""Patchless installer for Hermes-native integration shims."""

from __future__ import annotations

from pathlib import Path

from bridge.integrations.hermes_native.manifest import (
    HermesNativeManifest,
    IntegrationCheck,
    IntegrationReport,
    install_dir_for,
    manifest_path_for,
    wrapper_dir_for,
    write_manifest,
)
from bridge.runtime.config import load_config

WRAPPERS: dict[str, str] = {
    "send_message_tool_bridge.py": '''"""Generated Hermes WeChat Bridge send-message shim."""

from bridge.integrations.hermes_native.send_message_tool_shim import flush_queued, queue_status, send_message

__all__ = ["flush_queued", "queue_status", "send_message"]
''',
    "cron_bridge.py": '''"""Generated Hermes WeChat Bridge Cron notification shim."""

from bridge.integrations.hermes_native.cron_shim import notify_cron_failure, notify_cron_recovery

__all__ = ["notify_cron_failure", "notify_cron_recovery"]
''',
    "guardian_bridge.py": '''"""Generated Hermes WeChat Bridge Guardian notification shim."""

from bridge.integrations.hermes_native.guardian_shim import notify_guardian_incident, notify_guardian_recovery

__all__ = ["notify_guardian_incident", "notify_guardian_recovery"]
''',
}


def install_hermes_native(
    *,
    hermes_home: str | Path,
    config_path: str | Path,
    target_id: str,
    force: bool = False,
) -> IntegrationReport:
    """Install patchless shim files under a Hermes home directory."""

    hermes_root = Path(hermes_home).expanduser()
    if not hermes_root.is_absolute():
        hermes_root = hermes_root.resolve()
    config_file = Path(config_path).expanduser().resolve()
    checks: list[IntegrationCheck] = []

    hermes_root.mkdir(parents=True, exist_ok=True)
    checks.append(IntegrationCheck("hermes_home", True, str(hermes_root)))

    if not config_file.exists():
        checks.append(IntegrationCheck("bridge_config", False, f"config not found: {config_file}"))
        return _report(False, hermes_root, checks)
    load_config(config_file)
    checks.append(IntegrationCheck("bridge_config", True, str(config_file)))

    if not target_id.strip():
        checks.append(IntegrationCheck("target_id", False, "target id is required"))
        return _report(False, hermes_root, checks)
    checks.append(IntegrationCheck("target_id", True, "target id configured"))

    install_dir = install_dir_for(hermes_root)
    wrapper_dir = wrapper_dir_for(hermes_root)
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    checks.append(IntegrationCheck("install_dir", True, str(install_dir)))

    written_files: list[str] = []
    for filename, content in WRAPPERS.items():
        path = wrapper_dir / filename
        status = _write_file(path, content, force=force)
        written_files.append(str(path.relative_to(install_dir)))
        checks.append(IntegrationCheck(f"wrapper:{filename}", status[0], status[1]))

    if not all(check.ok for check in checks):
        return _report(False, hermes_root, checks)

    manifest = HermesNativeManifest.create(bridge_config=config_file, target_id=target_id.strip(), files=tuple(written_files))
    manifest_path = write_manifest(hermes_root, manifest)
    checks.append(IntegrationCheck("manifest", True, str(manifest_path)))
    return _report(True, hermes_root, checks, metadata={"manifest": manifest.to_dict(), "wrapper_dir": str(wrapper_dir)})


def _write_file(path: Path, content: str, *, force: bool) -> tuple[bool, str]:
    if path.exists() and path.read_text(encoding="utf-8") != content and not force:
        return False, f"exists with different content: {path} (rerun with --force to overwrite)"
    path.write_text(content, encoding="utf-8")
    return True, str(path)


def _report(
    ok: bool,
    hermes_root: Path,
    checks: list[IntegrationCheck],
    metadata: dict[str, object] | None = None,
) -> IntegrationReport:
    install_dir = install_dir_for(hermes_root)
    return IntegrationReport(
        ok=ok,
        hermes_home=str(hermes_root),
        install_dir=str(install_dir),
        manifest_path=str(manifest_path_for(hermes_root)),
        checks=tuple(checks),
        metadata=dict(metadata or {}),
    )

