# Contributing

Thank you for helping improve Hermes WeChat Bridge.

## Project Scope

This repository maintains one recommended path from Hermes Agent to WeChat. Keep changes focused on reliability, friendliness, diagnostics, and clear setup.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest
```

## Contribution Guidelines

- Prefer small, focused pull requests.
- Add or update tests for protocol, delivery, dedupe, diagnostics, and simulator behavior.
- Do not commit real tokens, chat IDs, logs, screenshots with private content, or runtime state.
- Keep examples runnable in mock mode.
- Keep public contracts additive unless a migration note is included.

## Pull Request Checklist

- [ ] Quickstart still works.
- [ ] `python -m pytest` passes.
- [ ] No real secrets or production identifiers are included.
- [ ] Docs are updated for user-visible behavior.
