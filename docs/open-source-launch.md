# Open Source Launch Checklist

Use this checklist before making the repository public.

## Repository Settings

- [ ] Create the public repository.
- [ ] Update badge and project URLs if the owner/name differs from `luSkyl/hermes-wechat-bridge`.
- [ ] Enable branch protection for `main`.
- [ ] Require CI before merging.
- [ ] Enable Dependabot alerts and security updates.
- [ ] Enable private vulnerability reporting.
- [ ] Enable CodeQL code scanning.
- [ ] Configure PyPI trusted publishing before uncommenting the publish step in `.github/workflows/release.yml`.

## Community Profile

- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `CONTRIBUTING.md`
- [ ] `SECURITY.md`
- [ ] Issue forms under `.github/ISSUE_TEMPLATE/`
- [ ] Pull request template under `.github/`
- [ ] `SUPPORT.md`, `GOVERNANCE.md`, `ROADMAP.md`, `CHANGELOG.md`

## Technical Gates

- [ ] `python -m pytest`
- [ ] `python -m ruff check .`
- [ ] `python -m compileall bridge simulator`
- [ ] `python -m bridge.cli doctor --config examples/minimal/config.yaml`
- [ ] `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json`
- [ ] `python scripts/check_release_ready.py`
- [ ] No real tokens, logs, private chat IDs, or runtime state.

## First Announcement

Suggested message:

> Hermes WeChat Bridge is an open-source golden path for connecting Hermes Agent to WeChat without polluting Hermes core or Hermes Web UI. It ships callback handling, message normalization, dedupe, retry, friendly replies, diagnostics, simulator fixtures, and contract tests.
