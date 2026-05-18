"""Safe logging helpers."""

from __future__ import annotations

SECRET_WORDS = ("token", "secret", "password", "authorization", "access_key")


def redact_mapping(data: dict[str, object]) -> dict[str, object]:
    redacted: dict[str, object] = {}
    for key, value in data.items():
        if any(word in key.lower() for word in SECRET_WORDS):
            redacted[key] = "<redacted>"
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted
