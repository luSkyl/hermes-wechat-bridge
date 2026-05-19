# Changelog

All notable changes to Hermes WeChat Bridge will be documented in this file.

The format follows the spirit of Keep a Changelog, and this project uses semantic versioning once public releases begin.

## [Unreleased]

## [0.1.1] - 2026-05-19

### Added

- Added Hermes Core distribution patches for persona-aware friendly gateway templates, cron/background friendly output, approval prompt copy, and local profile vault backups.

### Changed

- Updated the package version to `0.1.1`.
- Locked the distribution manifest to tag `v0.1.1`.

## [0.1.0] - 2026-05-19

### Added

- Promoted the Bridge package and Distribution Kit to the first stable GitHub release.
- Added a release workflow distribution bundle asset for users who want the installer, Core patches, and Web UI overlay from a tagged archive.

### Changed

- Updated the package version to `0.1.0`.
- Locked the distribution manifest to tag `v0.1.0`.

## [0.1.0-alpha.4] - 2026-05-18

### Added

- Hermes Native Integration Kit with patchless install/verify commands and generated shims for send-message, Cron, and Guardian notification paths.
- Service API endpoints for delivery status, governed notification sends, and queued notification flushes.
- `examples/hermes-native` clean-clone demo configuration, scripts, and smoke example.
- Contract tests for install/verify, generated wrappers, CLI, HTTP notification endpoints, and friendly-card shims.

### Changed

- Prepared the Python package version as `0.1.0a4` for the complete integration-kit alpha artifact.

### Distribution Kit

- Added `distribution/manifest.lock.json` for the locked Hermes Core, Hermes Web UI, and Bridge combination.
- Added `distribution/patches/hermes-core` with replayable Hermes runtime integration patches.
- Added `distribution/overlays/hermes-web-ui` with the Web UI source overlay and public replay metadata.
- Added Windows install, verify, build, start, stop, and rollback scripts for full distribution mode.
- Repositioned the README around Bridge-only and full distribution workflows.

## [0.1.0-alpha.3] - 2026-05-18

### Added

- File-backed Weixin Delivery Governor for outbound send-attempt budgeting, queueing, priority flush, and circuit breaking after rate-limit signals.
- Runtime notification adapters for `send_message_tool`-style sends, Cron failures/recoveries, Guardian incidents/recoveries, friendly-card templates, CLI `notify`, and CLI `flush`.
- Governor configuration keys in example configs and runtime config parsing.
- Contract tests for quota windows, rate-limit breaker behavior, half-open canary attempts, priority queueing, stale expiration, and friendly user-visible cards.

### Changed

- `WeChatSender` now routes outbound delivery through the governor before dry-run or real sender behavior.
- Prepared the Python package version as `0.1.0a3` for the next alpha artifact.

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
