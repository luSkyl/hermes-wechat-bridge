"""Configuration loading for the bridge."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bridge.protocol import ConfigurationError


@dataclass(frozen=True)
class WeChatConfig:
    token: str
    dry_run: bool = True
    app_id: str | None = None
    app_secret: str | None = None
    max_reply_chars: int = 1800
    governor_enabled: bool = True
    governor_state_dir: str | None = None
    governor_window_seconds: int = 60
    governor_initial_capacity: int = 3
    governor_min_capacity: int = 1
    governor_max_capacity: int = 20
    governor_max_flush_per_window: int = 3
    governor_queue_max_size: int = 500
    governor_base_backoff_seconds: int = 300
    governor_max_backoff_seconds: int = 3600
    governor_low_priority_ttl_seconds: int = 1800
    governor_default_ttl_seconds: int = 7200
    governor_high_priority_ttl_seconds: int = 21600
    governor_critical_ttl_seconds: int = 86400


@dataclass(frozen=True)
class HermesConfig:
    mode: str = "mock"
    endpoint: str | None = None
    timeout_seconds: float = 20.0


@dataclass(frozen=True)
class RuntimeConfig:
    dedupe_ttl_seconds: int = 300
    dedupe_state_dir: str | None = None
    retry_attempts: int = 2
    retry_backoff_seconds: float = 0.1
    request_timeout_seconds: float = 20.0
    service_api_token: str | None = None
    allow_unsigned_webhook: bool = False


@dataclass(frozen=True)
class BridgeConfig:
    name: str
    environment: str
    wechat: WeChatConfig
    hermes: HermesConfig
    runtime: RuntimeConfig


def load_config(path: str | Path) -> BridgeConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")
    data = _load_mapping(config_path)
    return parse_config(data)


def parse_config(data: dict[str, Any]) -> BridgeConfig:
    bridge_data = _section(data, "bridge")
    wechat_data = _section(data, "wechat")
    hermes_data = _section(data, "hermes")
    runtime_data = _section(data, "runtime")

    token = str(wechat_data.get("token") or "").strip()
    if not token:
        raise ConfigurationError("wechat.token is required")

    hermes_mode = str(hermes_data.get("mode", "mock")).strip().lower()
    if hermes_mode not in {"mock", "http"}:
        raise ConfigurationError("hermes.mode must be 'mock' or 'http'")
    endpoint = _optional_str(hermes_data.get("endpoint"))
    if hermes_mode == "http" and not endpoint:
        raise ConfigurationError("hermes.endpoint is required when hermes.mode is 'http'")

    return BridgeConfig(
        name=str(bridge_data.get("name", "hermes-wechat-bridge")),
        environment=str(bridge_data.get("environment", "local")),
        wechat=WeChatConfig(
            token=token,
            dry_run=_to_bool(wechat_data.get("dry_run", True)),
            app_id=_optional_str(wechat_data.get("app_id")),
            app_secret=_optional_str(wechat_data.get("app_secret")),
            max_reply_chars=_to_int(wechat_data.get("max_reply_chars", 1800), 1800),
            governor_enabled=_to_bool(wechat_data.get("governor_enabled", True)),
            governor_state_dir=_optional_str(wechat_data.get("governor_state_dir")),
            governor_window_seconds=_to_int(wechat_data.get("governor_window_seconds", 60), 60),
            governor_initial_capacity=_to_int(wechat_data.get("governor_initial_capacity", 3), 3),
            governor_min_capacity=_to_int(wechat_data.get("governor_min_capacity", 1), 1),
            governor_max_capacity=_to_int(wechat_data.get("governor_max_capacity", 20), 20),
            governor_max_flush_per_window=_to_int(wechat_data.get("governor_max_flush_per_window", 3), 3),
            governor_queue_max_size=_to_int(wechat_data.get("governor_queue_max_size", 500), 500),
            governor_base_backoff_seconds=_to_int(wechat_data.get("governor_base_backoff_seconds", 300), 300),
            governor_max_backoff_seconds=_to_int(wechat_data.get("governor_max_backoff_seconds", 3600), 3600),
            governor_low_priority_ttl_seconds=_to_int(wechat_data.get("governor_low_priority_ttl_seconds", 1800), 1800),
            governor_default_ttl_seconds=_to_int(wechat_data.get("governor_default_ttl_seconds", 7200), 7200),
            governor_high_priority_ttl_seconds=_to_int(wechat_data.get("governor_high_priority_ttl_seconds", 21600), 21600),
            governor_critical_ttl_seconds=_to_int(wechat_data.get("governor_critical_ttl_seconds", 86400), 86400),
        ),
        hermes=HermesConfig(
            mode=hermes_mode,
            endpoint=endpoint,
            timeout_seconds=_to_float(hermes_data.get("timeout_seconds", 20.0), 20.0),
        ),
        runtime=RuntimeConfig(
            dedupe_ttl_seconds=_to_int(runtime_data.get("dedupe_ttl_seconds", 300), 300),
            dedupe_state_dir=_optional_str(runtime_data.get("dedupe_state_dir")),
            retry_attempts=_to_int(runtime_data.get("retry_attempts", 2), 2),
            retry_backoff_seconds=_to_float(runtime_data.get("retry_backoff_seconds", 0.1), 0.1),
            request_timeout_seconds=_to_float(runtime_data.get("request_timeout_seconds", 20.0), 20.0),
            service_api_token=_optional_str(runtime_data.get("service_api_token")),
            allow_unsigned_webhook=_to_bool(runtime_data.get("allow_unsigned_webhook", False)),
        ),
    )


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_simple_yaml(path.read_text(encoding="utf-8"))

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ConfigurationError("Config root must be a mapping")
    return loaded


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section_name = line[:-1].strip()
            current_section = {}
            result[section_name] = current_section
            continue
        if current_section is None or ":" not in line:
            raise ConfigurationError("Simple config parser only supports top-level sections with scalar keys")
        key, value = line.strip().split(":", 1)
        current_section[key.strip()] = _parse_scalar(value.strip())
    return result


def _parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ConfigurationError(f"Missing config section: {name}")
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
