# Changelog

All notable changes to Hermes WeChat Bridge will be documented in this file.

The format follows the spirit of Keep a Changelog, and this project uses semantic versioning once public releases begin.

## [0.1.0-alpha.2] - 2026-05-18

### Added

- Release-note category configuration for generated GitHub release notes.
- Gated PyPI trusted-publishing workflow for future stable releases.
- Expanded public README positioning, quickstart, service API, and production guidance.

### Changed

- Prepared the Python package version as `0.1.0a2` for the next alpha artifact.

## [0.1.0-alpha.1] - 2026-05-18

### Added

- Initial Hermes to WeChat bridge MVP.
- WeChat callback parsing, signature verification, XML helpers, and dry-run sender.
- Hermes mock and HTTP client abstraction.
- Gateway router with session mapping, dedupe, retry, and friendly replies.
- Local simulator, examples, JSON schemas, docs, and contract tests.
- Service APIs for health, status, simulation, and controlled session messages.
- Open-source governance, CI, security, and release assets.

### Fixed

- Made CLI JSON output UTF-8 safe on Windows consoles that default to non-UTF-8 encodings.

## [0.1.0] - Unreleased

### Planned

- Stable package release after alpha validation and PyPI trusted publishing setup.
