"""Manifest models for Hermes-native integration installs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bridge import __version__

INSTALL_DIR_NAME = ".hermes-wechat-bridge"
MANIFEST_FILE_NAME = "integration.json"
WRAPPER_DIR_NAME = "shims"


@dataclass(frozen=True)
class IntegrationCheck:
    """One verifier/installer check result."""

    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


@dataclass(frozen=True)
class IntegrationReport:
    """Installer/verifier output suitable for CLI JSON."""

    ok: bool
    hermes_home: str
    install_dir: str
    manifest_path: str
    checks: tuple[IntegrationCheck, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "hermes_home": self.hermes_home,
            "install_dir": self.install_dir,
            "manifest_path": self.manifest_path,
            "checks": [check.to_dict() for check in self.checks],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class HermesNativeManifest:
    """Patchless install manifest written under a Hermes home directory."""

    version: str
    bridge_version: str
    bridge_config: str
    target_id: str
    installed_at: str
    files: tuple[str, ...]
    notes: tuple[str, ...] = ()

    @classmethod
    def create(cls, *, bridge_config: Path, target_id: str, files: tuple[str, ...]) -> HermesNativeManifest:
        return cls(
            version="1",
            bridge_version=__version__,
            bridge_config=str(bridge_config),
            target_id=target_id,
            installed_at=datetime.now(UTC).isoformat(timespec="seconds"),
            files=files,
            notes=(
                "Patchless integration: import generated shim modules from Hermes runtime hooks.",
                "All user-visible notifications must go through friendly-card templates and the Weixin governor.",
            ),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HermesNativeManifest:
        return cls(
            version=str(data.get("version") or "1"),
            bridge_version=str(data.get("bridge_version") or "unknown"),
            bridge_config=str(data.get("bridge_config") or ""),
            target_id=str(data.get("target_id") or ""),
            installed_at=str(data.get("installed_at") or ""),
            files=tuple(str(item) for item in data.get("files", ()) if str(item).strip()),
            notes=tuple(str(item) for item in data.get("notes", ()) if str(item).strip()),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "bridge_version": self.bridge_version,
            "bridge_config": self.bridge_config,
            "target_id": self.target_id,
            "installed_at": self.installed_at,
            "files": list(self.files),
            "notes": list(self.notes),
        }


def _normalize_home(hermes_home: str | Path) -> Path:
    path = Path(hermes_home).expanduser()
    return path if path.is_absolute() else path.resolve()


def install_dir_for(hermes_home: str | Path) -> Path:
    return _normalize_home(hermes_home) / INSTALL_DIR_NAME


def manifest_path_for(hermes_home: str | Path) -> Path:
    return install_dir_for(hermes_home) / MANIFEST_FILE_NAME


def wrapper_dir_for(hermes_home: str | Path) -> Path:
    return install_dir_for(hermes_home) / WRAPPER_DIR_NAME


def load_manifest(hermes_home: str | Path) -> HermesNativeManifest:
    path = manifest_path_for(hermes_home)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("integration manifest must be a JSON object")
    return HermesNativeManifest.from_dict(data)


def write_manifest(hermes_home: str | Path, manifest: HermesNativeManifest) -> Path:
    path = manifest_path_for(hermes_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

