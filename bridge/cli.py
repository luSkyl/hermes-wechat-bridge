"""Command-line interface for Hermes WeChat Bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bridge.hermes import HermesClient
from bridge.runtime.config import load_config
from bridge.runtime.diagnostics import run_diagnostics
from bridge.runtime.router import GatewayRouter
from bridge.server import serve
from bridge.wechat import WeChatAdapter, WeChatSender


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hermes-wechat-bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="check bridge configuration")
    doctor_parser.add_argument("--config", required=True, help="path to config YAML")

    simulate_parser = subparsers.add_parser("simulate", help="run a local simulated WeChat event")
    simulate_parser.add_argument("--config", required=True, help="path to config YAML")
    simulate_parser.add_argument("--event", required=True, help="path to sample event JSON")

    serve_parser = subparsers.add_parser("serve", help="run a minimal WeChat callback server")
    serve_parser.add_argument("--config", required=True, help="path to config YAML")
    serve_parser.add_argument("--host", default="127.0.0.1", help="bind host")
    serve_parser.add_argument("--port", type=int, default=8787, help="bind port")

    args = parser.parse_args(argv)
    if args.command == "doctor":
        return _doctor(args.config)
    if args.command == "simulate":
        return _simulate(args.config, args.event)
    if args.command == "serve":
        serve(args.config, host=args.host, port=args.port)
        return 0
    parser.error("unknown command")
    return 2


def _doctor(config_path: str) -> int:
    config = load_config(config_path)
    result = run_diagnostics(config)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def _simulate(config_path: str, event_path: str) -> int:
    config = load_config(config_path)
    payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    adapter = WeChatAdapter(config.wechat)
    event = adapter.normalize(payload)
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=WeChatSender(config.wechat))
    result = router.handle_event(event)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status in {"delivered", "duplicate"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
