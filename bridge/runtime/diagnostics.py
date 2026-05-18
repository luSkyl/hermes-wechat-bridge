"""Configuration diagnostics."""

from __future__ import annotations

from bridge.runtime.config import BridgeConfig
from bridge.runtime.health import HealthCheckResult


def run_diagnostics(config: BridgeConfig) -> HealthCheckResult:
    checks: dict[str, bool] = {
        "bridge_name": bool(config.name.strip()),
        "wechat_token": bool(config.wechat.token.strip()),
        "hermes_mode": config.hermes.mode in {"mock", "http"},
        "hermes_endpoint": config.hermes.mode == "mock" or bool(config.hermes.endpoint),
        "retry_attempts": config.runtime.retry_attempts >= 1,
        "dedupe_ttl": config.runtime.dedupe_ttl_seconds >= 1,
    }
    messages = [name for name, ok in checks.items() if not ok]
    return HealthCheckResult(ok=all(checks.values()), checks=checks, messages=messages)
