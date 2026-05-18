from bridge.runtime.config import load_config
from bridge.runtime.service import BridgeService


def test_bridge_service_exposes_web_ui_safe_status() -> None:
    service = BridgeService(load_config("examples/minimal/config.yaml"))

    health = service.health()
    status = service.status()

    assert health["ok"] is True
    assert status == {
        "ok": True,
        "service": "hermes-wechat-bridge",
        "environment": "local",
        "hermes_mode": "mock",
        "wechat_dry_run": True,
    }


def test_bridge_service_simulate_matches_gateway_contract() -> None:
    service = BridgeService(load_config("examples/minimal/config.yaml"))

    result = service.simulate(
        {
            "MsgId": "service-sim-1",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "Content": "hello",
        }
    )

    assert result.status == "delivered"
    assert result.session_id == "wechat:bridge:user-1"
    assert result.delivery is not None
    assert result.delivery.ok is True


def test_bridge_service_session_message_is_dry_run_delivery() -> None:
    service = BridgeService(load_config("examples/minimal/config.yaml"))

    result = service.send_session_message("wechat:bridge:user-1", "manual reply")

    assert result.ok is True
    assert result.delivery_id == "dry-run:bridge:user-1"
    assert result.metadata["request"]["text"] == "manual reply"
