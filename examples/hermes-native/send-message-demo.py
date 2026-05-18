from __future__ import annotations

import json
import sys
from pathlib import Path

from bridge.integrations.hermes_native import (
    flush_queued,
    notify_cron_failure,
    notify_cron_recovery,
    notify_guardian_incident,
    notify_guardian_recovery,
    queue_status,
    send_message,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

CONFIG = Path(__file__).with_name("config.yaml")
TARGET = "wxid_home"

for payload in (
    send_message(config_path=CONFIG, target_id=TARGET, title="上游模型已恢复", text="模型恢复后需要重新执行定时任务。"),
    notify_cron_failure(config_path=CONFIG, target_id=TARGET, job_name="morning-report", reason="采集脚本没有按时完成"),
    notify_cron_recovery(config_path=CONFIG, target_id=TARGET, job_name="morning-report"),
    notify_guardian_incident(config_path=CONFIG, target_id=TARGET, name="upstream-model", state="failed", reason="健康检查失败"),
    notify_guardian_recovery(config_path=CONFIG, target_id=TARGET, name="upstream-model"),
    queue_status(config_path=CONFIG),
    flush_queued(config_path=CONFIG, target_id=TARGET, limit=3),
):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
