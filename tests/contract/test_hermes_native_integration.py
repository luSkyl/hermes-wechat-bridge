from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from bridge.cli import main
from bridge.integrations.hermes_native import (
    flush_queued,
    install_hermes_native,
    notify_cron_failure,
    notify_cron_recovery,
    notify_guardian_incident,
    notify_guardian_recovery,
    queue_status,
    send_message,
    verify_hermes_native,
)
from bridge.integrations.hermes_native.manifest import wrapper_dir_for


def test_install_and_verify_hermes_native_integration(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    config_path = Path("examples/minimal/config.yaml").resolve()

    install = install_hermes_native(
        hermes_home=hermes_home,
        config_path=config_path,
        target_id="wxid_home",
    )
    verify = verify_hermes_native(hermes_home=hermes_home)

    assert install.ok is True
    assert verify.ok is True
    assert (hermes_home / ".hermes-wechat-bridge" / "integration.json").exists()
    assert (hermes_home / ".hermes-wechat-bridge" / "shims" / "send_message_tool_bridge.py").exists()


def test_generated_wrapper_modules_are_importable_and_governed(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    config_path = Path("examples/minimal/config.yaml").resolve()
    install_hermes_native(hermes_home=hermes_home, config_path=config_path, target_id="wxid_home")
    sys.path.insert(0, str(wrapper_dir_for(hermes_home)))
    try:
        module = importlib.import_module("send_message_tool_bridge")
        result = module.send_message(config_path=config_path, target_id="wxid_home", text="hello")
    finally:
        sys.path.remove(str(wrapper_dir_for(hermes_home)))
        sys.modules.pop("send_message_tool_bridge", None)

    assert result["ok"] is True
    assert result["metadata"]["governed"] is True
    assert "📌 当前情况" in result["metadata"]["request"]["text"]


def test_send_message_cron_and_guardian_shims_use_friendly_cards(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HERMES_WECHAT_BRIDGE_STATE_DIR", str(tmp_path / "state"))
    config_path = Path("examples/minimal/config.yaml").resolve()

    direct = send_message(config_path=config_path, target_id="wxid_home", text="Traceback ret=-2 raw")
    cron_fail = notify_cron_failure(
        config_path=config_path,
        target_id="wxid_home",
        job_name="morning-report",
        reason="RuntimeError ret=-2",
    )
    cron_recovery = notify_cron_recovery(config_path=config_path, target_id="wxid_home", job_name="morning-report")
    guardian_fail = notify_guardian_incident(
        config_path=config_path,
        target_id="wxid_home",
        name="upstream-model",
        state="failed",
        reason="Traceback ret=-2",
    )
    guardian_recovery = notify_guardian_recovery(config_path=config_path, target_id="wxid_home", name="upstream-model")

    for result in (direct, cron_fail, cron_recovery, guardian_fail, guardian_recovery):
        assert result["ok"] is True
        text = result["metadata"]["request"]["text"]
        assert "📌 当前情况" in text
        assert "ret=-2" not in text
        assert "Traceback" not in text


def test_queue_status_and_flush_shims_are_safe(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HERMES_WECHAT_BRIDGE_STATE_DIR", str(tmp_path / "state"))
    config_path = Path("examples/minimal/config.yaml").resolve()

    status = queue_status(config_path=config_path)
    flush = flush_queued(config_path=config_path, target_id="wxid_home", limit=3)

    assert status["enabled"] is True
    assert flush == {"ok": True, "count": 0, "results": []}


def test_cli_install_verify_notify_flush_and_queue_status(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("HERMES_WECHAT_BRIDGE_STATE_DIR", str(tmp_path / "state"))
    hermes_home = tmp_path / "hermes-home"
    config_path = "examples/minimal/config.yaml"

    assert main(["install-hermes-native", "--hermes-home", str(hermes_home), "--config", config_path, "--target", "wxid_home"]) == 0
    install_payload = json.loads(capsys.readouterr().out)
    assert install_payload["ok"] is True

    assert main(["verify-hermes-native", "--hermes-home", str(hermes_home)]) == 0
    verify_payload = json.loads(capsys.readouterr().out)
    assert verify_payload["ok"] is True

    assert main(["queue-status", "--config", config_path]) == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["enabled"] is True

    assert main(["notify", "--config", config_path, "--target", "wxid_home", "--text", "hello", "--priority", "high"]) == 0
    notify_payload = json.loads(capsys.readouterr().out)
    assert notify_payload["ok"] is True
    assert "📌 当前情况" in notify_payload["metadata"]["request"]["text"]

    assert main(["flush", "--config", config_path, "--target", "wxid_home", "--limit", "3"]) == 0
    flush_payload = json.loads(capsys.readouterr().out)
    assert flush_payload["ok"] is True
