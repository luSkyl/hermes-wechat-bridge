from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_weixin_governor_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_WECHAT_BRIDGE_STATE_DIR", str(tmp_path / "bridge-state"))
