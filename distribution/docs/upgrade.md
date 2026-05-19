# Upgrade Playbook

## Web UI

1. Pick the new official Hermes Web UI ref.
2. Run `distribution/scripts/build-web-ui.ps1` with the new ref and a new local release name.
3. Resolve overlay conflicts in `distribution/overlays/hermes-web-ui`, not in a runtime release directory.
4. Run focused tests, build, and shadow smoke before switching the runtime manifest.
5. Keep the previous local release and the official baseline as rollback targets.

## Hermes Core

1. Clone the new upstream Hermes Core ref into a disposable worktree.
2. Run `distribution/scripts/apply-core-patches.ps1 -CheckOnly` first.
3. Resolve conflicts by updating patches in `distribution/patches/hermes-core`.
4. Run focused core tests and runtime verification.
5. Promote only after the patched core is reproducible from a clean checkout.

## Bridge

1. Keep `pyproject.toml` version and Git tag aligned.
2. Run ruff, pytest, py_compile, and release checks.
3. Publish alpha/rc tags before stable releases.
