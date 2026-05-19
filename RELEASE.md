# Release Process

Use this process for public releases.

Hermes WeChat Bridge publishes GitHub Releases on every `v*.*.*` tag. Tags that contain a hyphen, such as `v0.1.0-alpha.1`, are marked as GitHub prereleases. Stable tags, such as `v0.1.0`, can publish to PyPI after trusted publishing is configured and explicitly enabled.

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
- [ ] README.md quickstart still matches behavior.
- [ ] distribution/scripts/verify.ps1 passes against an existing Hermes workspace.
- [ ] Distribution manifest and patch/overlay hashes are current.
- [ ] GitHub Release includes wheel, sdist, and distribution zip assets.

## Tagging

### Alpha or RC Releases

Use prerelease tags while the public contract is still being validated:

```powershell
git tag -a v0.1.1-alpha.1 -m "v0.1.1-alpha.1"
git push origin v0.1.1-alpha.1
```

Prerelease tags create GitHub prereleases with wheel and source distribution assets, but they do not publish to PyPI.

### Stable Releases

```powershell
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

## Publishing

The release workflow always builds Python distribution artifacts plus a `hermes-wechat-distribution-<tag>.zip` bundle and attaches them to GitHub Releases.

PyPI publishing is intentionally gated and uses trusted publishing only. It runs only when all of these are true:

- The pushed tag is a stable tag without a hyphen, for example `v0.1.0`.
- The repository variable `PUBLISH_TO_PYPI` is set to `true`.
- The GitHub environment `pypi` exists.
- The PyPI project has a trusted publisher for this repository and workflow.

Configure PyPI trusted publishing with these values:

| Field | Value |
|---|---|
| PyPI project | `hermes-wechat-bridge` |
| Owner | `luSkyl` |
| Repository | `hermes-wechat-bridge` |
| Workflow | `release.yml` |
| Environment | `pypi` |

If the PyPI project does not exist yet, create it with PyPI's pending publisher flow, or publish the first stable release only after the trusted publisher is registered.

Before enabling PyPI publishing, update `pyproject.toml` project URLs if the public repository owner/name differs.

## Release Notes

GitHub release notes are generated from `.github/release.yml`. Keep PR labels meaningful so releases are grouped into breaking changes, features, fixes, WeChat/runtime changes, docs, tests, and CI.

`CHANGELOG.md` remains the human-curated changelog. Update it before cutting a stable release.

## Rollback

- Withdraw or mark a broken release in GitHub Releases.
- Publish a patch release with a clear changelog entry.
- Rotate any exposed credentials immediately.
