# Roadmap

## v0.1: Bridge and Distribution Foundation

- Stable Hermes to WeChat bridge MVP.
- WeChat callback verification, XML/JSON parsing, and dry-run delivery.
- Dedupe, retry, friendly formatting, diagnostics, simulator, and contract tests.
- CI, security scanning, issue templates, release process, and governance docs.
- Full distribution kit layout with locked manifest, Hermes Core patches, Hermes Web UI overlay, and Windows verification scripts.

## v0.1 Alpha Line

- `v0.1.0-alpha.4`: first release that positions the repository as both Bridge package and Distribution Kit.
- `v0.1.0-alpha.5`: clean-directory distribution verification and installer hardening.
- `v0.1.0-alpha.6`: full install, verify, start, stop, and rollback gates pass without private local state.
- `v0.1.0-rc.1`: release candidate after a fresh Windows workspace reproduction.

## v0.2: Production Hardening

- Real WeChat outbound sender adapter.
- Persistent dedupe/session store option.
- Structured logs with redaction.
- More detailed diagnostics for callback, Hermes endpoint, and delivery failures.
- Installer support for upgrading an existing distribution in place.

## v0.3: Operator Experience

- Web UI read-only integration examples.
- Metrics endpoint for delivery and failure rates.
- Replay-safe incident bundles with automatic redaction.
- Distribution health dashboard contract.

## Later

- Optional adapter protocol extraction if multiple bridges reuse the same contracts.
- Split distribution into a separate repository only if the single-project layout becomes too heavy.
