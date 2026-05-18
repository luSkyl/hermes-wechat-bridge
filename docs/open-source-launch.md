# Open Source Launch Checklist

Use this checklist before making the repository public.

## Repository Settings

- [x] Create the public repository.
- [x] Update badge and project URLs for `luSkyl/hermes-wechat-bridge`.
- [x] Enable branch protection for `main`.
- [x] Require CI before merging.
- [x] Enable Dependabot alerts and security updates.
- [x] Enable private vulnerability reporting.
- [x] Enable CodeQL code scanning.
- [ ] Configure PyPI trusted publishing and set `PUBLISH_TO_PYPI=true` before stable PyPI releases.

## Community Profile

- [x] `README.md`
- [x] `LICENSE`
- [x] `CODE_OF_CONDUCT.md`
- [x] `CONTRIBUTING.md`
- [x] `SECURITY.md`
- [x] Issue forms under `.github/ISSUE_TEMPLATE/`
- [x] Pull request template under `.github/`
- [x] `SUPPORT.md`, `GOVERNANCE.md`, `ROADMAP.md`, `CHANGELOG.md`

## Technical Gates

- [x] `python -m pytest`
- [x] `python -m ruff check .`
- [x] `python -m compileall bridge simulator`
- [x] `python -m bridge.cli doctor --config examples/minimal/config.yaml`
- [x] `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json`
- [x] `python scripts/check_release_ready.py`
- [x] No real tokens, logs, private chat IDs, or runtime state.

## Release Status

- [x] `v0.1.0-alpha.1` prerelease created.
- [x] GitHub release artifacts uploaded.
- [x] Release notes generation configured in `.github/release.yml`.
- [x] PyPI trusted-publishing workflow is present but gated until PyPI is configured.

## First Announcement

Suggested message:

> Hermes WeChat Bridge is an open-source golden path for connecting Hermes Agent to WeChat without polluting Hermes core or Hermes Web UI. It ships callback handling, message normalization, dedupe, retry, friendly replies, diagnostics, simulator fixtures, and contract tests.
