"""Verifier for Hermes-native integration installs."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from bridge.integrations.hermes_native.manifest import (
    IntegrationCheck,
    IntegrationReport,
    install_dir_for,
    load_manifest,
    manifest_path_for,
)
from bridge.runtime.config import load_config
from bridge.runtime.service import BridgeService

REQUIRED_MODULES = (
    "bridge.integrations.hermes_native.send_message_tool_shim",
    "bridge.integrations.hermes_native.cron_shim",
    "bridge.integrations.hermes_native.guardian_shim",
)


def verify_hermes_native(*, hermes_home: str | Path) -> IntegrationReport:
    """Verify that a Hermes home has a usable patchless bridge integration."""

    hermes_root = Path(hermes_home).expanduser()
    if not hermes_root.is_absolute():
        hermes_root = hermes_root.resolve()
    install_dir = install_dir_for(hermes_root)
    checks: list[IntegrationCheck] = []

    checks.append(IntegrationCheck("hermes_home", hermes_root.exists(), str(hermes_root)))
    checks.append(IntegrationCheck("install_dir", install_dir.exists(), str(install_dir)))

    manifest_path = manifest_path_for(hermes_root)
    if not manifest_path.exists():
        checks.append(IntegrationCheck("manifest", False, f"missing: {manifest_path}"))
        return _report(False, hermes_root, checks)

    try:
        manifest = load_manifest(hermes_root)
        checks.append(IntegrationCheck("manifest", True, str(manifest_path)))
    except Exception as exc:  # noqa: BLE001 - verifier reports safe diagnostic
        checks.append(IntegrationCheck("manifest", False, str(exc)))
        return _report(False, hermes_root, checks)

    config_path = Path(manifest.bridge_config).expanduser()
    if not config_path.exists():
        checks.append(IntegrationCheck("bridge_config", False, f"missing: {config_path}"))
    else:
        try:
            service = BridgeService(load_config(config_path))
            checks.append(IntegrationCheck("bridge_config", True, str(config_path)))
            checks.append(IntegrationCheck("delivery_governor", True, str(service.delivery_status().get("status"))))
        except Exception as exc:  # noqa: BLE001 - verifier reports safe diagnostic
            checks.append(IntegrationCheck("bridge_config", False, str(exc)))

    checks.append(IntegrationCheck("target_id", bool(manifest.target_id.strip()), "target id configured"))

    for file_name in manifest.files:
        path = install_dir / file_name
        checks.append(IntegrationCheck(f"file:{file_name}", path.exists(), str(path)))

    for module_name in REQUIRED_MODULES:
        try:
            import_module(module_name)
            checks.append(IntegrationCheck(f"import:{module_name.rsplit('.', 1)[-1]}", True, module_name))
        except Exception as exc:  # noqa: BLE001 - verifier reports safe diagnostic
            checks.append(IntegrationCheck(f"import:{module_name.rsplit('.', 1)[-1]}", False, str(exc)))

    ok = all(check.ok for check in checks)
    return _report(ok, hermes_root, checks, metadata={"manifest": manifest.to_dict()})


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

