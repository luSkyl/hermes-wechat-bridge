import io
import sys
from pathlib import Path

from bridge.cli import _print_json, main
from bridge.hermes import HermesClient
from bridge.runtime.config import load_config
from bridge.runtime.router import GatewayRouter
from bridge.wechat import WeChatAdapter, WeChatSender

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "examples" / "minimal" / "config.yaml"
TEXT_EVENT = ROOT / "simulator" / "sample_events" / "text.json"


def test_doctor_passes_for_minimal_config() -> None:
    config = load_config(CONFIG)

    assert config.name == "hermes-wechat-bridge"
    assert config.hermes.mode == "mock"
    assert config.wechat.dry_run is True


def test_router_delivers_mock_hermes_reply() -> None:
    config = load_config(CONFIG)
    adapter = WeChatAdapter(config.wechat)
    event = adapter.normalize(
        {
            "MsgId": "flow-1",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "Content": "hello Hermes",
        }
    )
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=WeChatSender(config.wechat))

    result = router.handle_event(event)

    assert result.status == "delivered"
    assert result.session_id == "wechat:bridge:user-1"
    assert result.delivery is not None
    assert result.delivery.ok is True
    assert "Hermes mock reply" in str(result.reply_text)


def test_router_deduplicates_replayed_event() -> None:
    config = load_config(CONFIG)
    adapter = WeChatAdapter(config.wechat)
    event = adapter.normalize(
        {
            "MsgId": "flow-duplicate",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "Content": "hello Hermes",
        }
    )
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=WeChatSender(config.wechat))

    first = router.handle_event(event)
    second = router.handle_event(event)

    assert first.status == "delivered"
    assert second.status == "duplicate"
    assert second.delivery is None


def test_cli_doctor_and_simulate_pass() -> None:
    assert main(["doctor", "--config", str(CONFIG)]) == 0
    assert main(["simulate", "--config", str(CONFIG), "--event", str(TEXT_EVENT)]) == 0


def test_cli_json_output_survives_non_utf8_stdout(monkeypatch) -> None:
    raw_output = io.BytesIO()
    cp1252_stdout = io.TextIOWrapper(raw_output, encoding="cp1252", write_through=True)
    monkeypatch.setattr(sys, "stdout", cp1252_stdout)

    _print_json({"reply_text": "你好 Hermes"})
    cp1252_stdout.flush()

    assert "你好 Hermes" in raw_output.getvalue().decode("utf-8")
