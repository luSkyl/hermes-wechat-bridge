# Release Process

Use this process for public releases.

## Pre-Release Checklist

- [ ] `python -m pytest` passes.
- [ ] `python -m ruff check .` passes.
- [ ] `python -m compileall bridge simulator` passes.
- [ ] `python -m build` succeeds.
- [ ] `python -m twine check dist/*` succeeds.
- [ ] `python -m bridge.cli doctor --config examples/minimal/config.yaml` passes.
- [ ] `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json` passes.
- [ ] Secret scan shows no real credentials.
- [ ] `CHANGELOG.md` includes the release notes.
- [ ] `README.md` quickstart still matches behavior.

## Tagging

```powershell
git tag v0.1.0
git push origin v0.1.0
```

## Publishing

The package workflow builds distribution artifacts on tags. PyPI publishing should use trusted publishing after the project owner configures the PyPI project and GitHub environment.

Before enabling PyPI publishing, update `pyproject.toml` project URLs if the public repository owner/name differs.

## Rollback

- Withdraw or mark a broken release in GitHub Releases.
- Publish a patch release with a clear changelog entry.
- Rotate any exposed credentials immediately.
