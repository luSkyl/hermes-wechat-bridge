"""Command-line interface for Hermes WeChat Bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bridge.hermes import HermesClient
from bridge.integrations.hermes_native import install_hermes_native, verify_hermes_native
from bridge.runtime.config import load_config
from bridge.runtime.diagnostics import run_diagnostics
from bridge.runtime.router import GatewayRouter
from bridge.runtime.service import BridgeService
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

    notify_parser = subparsers.add_parser("notify", help="send or queue a governed friendly-card notification")
    notify_parser.add_argument("--config", required=True, help="path to config YAML")
    notify_parser.add_argument("--target", required=True, help="WeChat recipient / conversation id")
    notify_parser.add_argument("--text", required=True, help="notification text; wrapped into the friendly-card template")
    notify_parser.add_argument("--title", default="通知已接收", help="friendly-card title")
    notify_parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "critical"])

    flush_parser = subparsers.add_parser("flush", help="flush queued governed notifications for a target")
    flush_parser.add_argument("--config", required=True, help="path to config YAML")
    flush_parser.add_argument("--target", required=True, help="WeChat recipient / conversation id")
    flush_parser.add_argument("--limit", type=int, default=None, help="maximum queued notifications to send")

    queue_parser = subparsers.add_parser("queue-status", help="show safe Weixin delivery-governor queue status")
    queue_parser.add_argument("--config", required=True, help="path to config YAML")

    install_parser = subparsers.add_parser("install-hermes-native", help="install patchless Hermes native integration shims")
    install_parser.add_argument("--hermes-home", required=True, help="Hermes home/workspace directory to receive shim manifest")
    install_parser.add_argument("--config", required=True, help="bridge config YAML used by the generated shims")
    install_parser.add_argument("--target", required=True, help="default WeChat recipient / conversation id")
    install_parser.add_argument("--force", action="store_true", help="overwrite generated shim files if they differ")

    verify_parser = subparsers.add_parser("verify-hermes-native", help="verify a patchless Hermes native integration install")
    verify_parser.add_argument("--hermes-home", required=True, help="Hermes home/workspace directory containing integration.json")

    args = parser.parse_args(argv)
    if args.command == "doctor":
        return _doctor(args.config)
    if args.command == "simulate":
        return _simulate(args.config, args.event)
    if args.command == "serve":
        serve(args.config, host=args.host, port=args.port)
        return 0
    if args.command == "notify":
        return _notify(args.config, args.target, args.text, args.title, args.priority)
    if args.command == "flush":
        return _flush(args.config, args.target, args.limit)
    if args.command == "queue-status":
        return _queue_status(args.config)
    if args.command == "install-hermes-native":
        return _install_hermes_native(args.hermes_home, args.config, args.target, args.force)
    if args.command == "verify-hermes-native":
        return _verify_hermes_native(args.hermes_home)
    parser.error("unknown command")
    return 2


def _doctor(config_path: str) -> int:
    config = load_config(config_path)
    result = run_diagnostics(config)
    _print_json(result.to_dict())
    return 0 if result.ok else 1


def _simulate(config_path: str, event_path: str) -> int:
    config = load_config(config_path)
    payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    adapter = WeChatAdapter(config.wechat)
    event = adapter.normalize(payload)
    router = GatewayRouter(config=config, hermes=HermesClient(config.hermes), sender=WeChatSender(config.wechat))
    result = router.handle_event(event)
    _print_json(result.to_dict())
    return 0 if result.status in {"delivered", "duplicate"} else 1


def _notify(config_path: str, target: str, text: str, title: str, priority: str) -> int:
    service = BridgeService(load_config(config_path))
    result = service.send_notification(target_id=target, text=text, title=title, priority=priority)
    _print_json(result.to_dict())
    return 0 if result.ok else 1


def _flush(config_path: str, target: str, limit: int | None) -> int:
    service = BridgeService(load_config(config_path))
    results = service.flush_notifications(target_id=target, limit=limit)
    payload = {"ok": all(item.ok for item in results), "count": len(results), "results": [item.to_dict() for item in results]}
    _print_json(payload)
    return 0 if payload["ok"] else 1


def _queue_status(config_path: str) -> int:
    service = BridgeService(load_config(config_path))
    _print_json(service.delivery_status())
    return 0


def _install_hermes_native(hermes_home: str, config_path: str, target: str, force: bool) -> int:
    report = install_hermes_native(hermes_home=hermes_home, config_path=config_path, target_id=target, force=force)
    _print_json(report.to_dict())
    return 0 if report.ok else 1


def _verify_hermes_native(hermes_home: str) -> int:
    report = verify_hermes_native(hermes_home=hermes_home)
    _print_json(report.to_dict())
    return 0 if report.ok else 1


def _print_json(payload: dict[str, object]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    try:
        sys.stdout.write(f"{text}\n")
    except UnicodeEncodeError:
        output = f"{text}\n".encode()
        stdout_buffer = getattr(sys.stdout, "buffer", None)
        if stdout_buffer is None:
            sys.stdout.write(output.decode("ascii", errors="backslashreplace"))
            return
        stdout_buffer.write(output)
        stdout_buffer.flush()


if __name__ == "__main__":
    raise SystemExit(main())
