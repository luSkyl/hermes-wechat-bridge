# Roadmap

## v0.1: Open-Source Foundation

- Stable Hermes to WeChat bridge MVP.
- WeChat callback verification, XML/JSON parsing, and dry-run delivery.
- Dedupe, retry, friendly formatting, diagnostics, simulator, and contract tests.
- CI, security scanning, issue templates, release process, and governance docs.

## v0.2: Production Hardening

- Real WeChat outbound sender adapter.
- Persistent dedupe/session store option.
- Structured logs with redaction.
- More detailed diagnostics for callback, Hermes endpoint, and delivery failures.

## v0.3: Operator Experience

- Web UI read-only integration examples.
- Metrics endpoint for delivery and failure rates.
- Replay-safe incident bundles with automatic redaction.

## Later

- Optional adapter protocol extraction if multiple bridges reuse the same contracts.
- Additional deployment examples after the golden path is stable.
