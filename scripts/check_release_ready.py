"""Local release readiness checks."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"xox[baprs]-"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"ghp_[0-9A-Za-z]{36}"),
]


def main() -> int:
    checks = [
        [sys.executable, "-m", "pytest"],
        [sys.executable, "-m", "compileall", "bridge", "simulator"],
        [sys.executable, "-m", "bridge.cli", "doctor", "--config", "examples/minimal/config.yaml"],
        [
            sys.executable,
            "-m",
            "bridge.cli",
            "simulate",
            "--config",
            "examples/minimal/config.yaml",
            "--event",
            "simulator/sample_events/text.json",
        ],
    ]
    for command in checks:
        print(f":: running {' '.join(command)}")
        subprocess.run(command, cwd=ROOT, check=True)
    scan_secrets()
    print("release readiness checks passed")
    return 0


def scan_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                relative = path.relative_to(ROOT)
                raise SystemExit(f"potential secret matched {pattern.pattern!r} in {relative}")


def should_skip(path: Path) -> bool:
    if path.resolve() == Path(__file__).resolve():
        return True
    ignored_parts = {".git", ".pytest_cache", "__pycache__", "dist", "build", ".venv", "venv"}
    return any(part in ignored_parts for part in path.parts)


if __name__ == "__main__":
    raise SystemExit(main())
