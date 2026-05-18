"""WeChat webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac


def build_signature(token: str, timestamp: str, nonce: str) -> str:
    parts = sorted([token, timestamp, nonce])
    return hashlib.sha1("".join(parts).encode("utf-8")).hexdigest()


def verify_signature(token: str, timestamp: str, nonce: str, signature: str) -> bool:
    expected = build_signature(token=token, timestamp=timestamp, nonce=nonce)
    return hmac.compare_digest(expected, signature)
