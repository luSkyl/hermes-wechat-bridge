"""Integration helpers for patchless Hermes-native notification wiring."""

from .cron_shim import notify_cron_failure, notify_cron_recovery
from .guardian_shim import notify_guardian_incident, notify_guardian_recovery
from .installer import install_hermes_native
from .manifest import HermesNativeManifest, IntegrationCheck, IntegrationReport
from .send_message_tool_shim import flush_queued, queue_status, send_message
from .verifier import verify_hermes_native

__all__ = [
    "HermesNativeManifest",
    "IntegrationCheck",
    "IntegrationReport",
    "flush_queued",
    "install_hermes_native",
    "notify_cron_failure",
    "notify_cron_recovery",
    "notify_guardian_incident",
    "notify_guardian_recovery",
    "queue_status",
    "send_message",
    "verify_hermes_native",
]
