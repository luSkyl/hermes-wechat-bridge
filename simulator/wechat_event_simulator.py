"""Local WeChat event simulator."""

from __future__ import annotations

import json
from pathlib import Path

from bridge.hermes import HermesClient
from bridge.runtime.config import load_config
from bridge.runtime.router import GatewayRouter
from bridge.wechat import WeChatAdapter, WeChatSender


def simulate(config_path: str | Path, event_path: str | Path) -> dict[str, object]:
    config = load_config(config_path)
    payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    event = WeChatAdapter(config.wechat).normalize(payload)
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=WeChatSender(config.wechat))
    return router.handle_event(event).to_dict()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Replay a sample WeChat event through the bridge")
    parser.add_argument("--config", required=True)
    parser.add_argument("--event", required=True)
    args = parser.parse_args()
    print(json.dumps(simulate(args.config, args.event), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
