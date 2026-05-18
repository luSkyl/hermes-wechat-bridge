# Task Plan: Hermes WeChat Bridge

## Goal

Create a clean open-source MVP that lets users follow one recommended path to build a stable, friendly Hermes Agent to WeChat bridge.

## Scope

- New project only: do not copy private runtime state, tokens, logs, or existing production traces.
- Deliver docs, protocol models, bridge runtime, simulator, examples, and tests.
- Optimize for a 15-30 minute quickstart and clear troubleshooting.

## Phases

| Phase | Status | Output |
|---|---|---|
| 1. Project skeleton and planning | complete | Repo layout, planning files, baseline metadata |
| 2. Documentation and diagrams | complete | README, architecture, flow, failure modes, setup docs |
| 3. Protocol and runtime code | complete | Message protocol, WeChat adapter, Hermes client, router, reliability helpers |
| 4. Simulator and examples | complete | Local event simulator, sample events, minimal configs/scripts |
| 5. Tests and packaging | complete | Pytest suite, pyproject, CLI entry, .env.example |
| 6. Verification and closeout | complete | Test evidence, security review note, final summary |
| 7. Decoupling governance plan | complete | Sync strategy, migration map, compatibility matrix, upgrade playbooks |
| 8. Stable service API | complete | Health/status/simulate/message endpoints for Web UI and operations |
| 9. Compatibility tests | complete | Hermes/Web UI/Bridge contract tests and upgrade smoke checks |
| 10. Final decoupling closeout | complete | Updated evidence, security review, cache cleanup |
| 11. Open-source launch hardening | complete | Community profile, CI, security scans, release process, launch docs |

## Acceptance Criteria

- `python -m pytest` passes in the project.
- `python -m bridge.cli doctor --config examples/minimal/config.yaml` reports a usable demo configuration.
- `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json` runs an end-to-end simulated message flow.
- Docs include gateway diagrams, quickstart, configuration, troubleshooting, security model, and production checklist.
- No real secrets or runtime state are committed.
- Three-project boundary is documented: Hermes, Hermes Web UI, and hermes-wechat-bridge.
- Bridge exposes stable operational APIs so Web UI can observe it without owning runtime logic.
- Compatibility tests prove Hermes/Web UI upgrades only need contract validation.
- Repository includes mature open-source project assets: issue templates, PR template, CI, CodeQL, Dependabot, Scorecard, release workflow, support, governance, changelog, and launch checklist.

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| RCCP script missing | task bootstrap | Recorded `RCCP_NOT_FOUND`; using project planning files as fallback evidence chain. |
| HTTP session message endpoint returned 400 | contract test attempt 1 | Fixed `_build_handler()` to keep a shared `sender` instance for service API routes. |

## Verification Evidence

| Check | Result |
|---|---|
| `python -m pytest` | pass: 13 passed |
| `python -m pytest` after decoupling | pass: 21 passed |
| `python -m bridge.cli --help` | pass: doctor/simulate/serve visible |
| `python -m bridge.cli doctor --config examples/minimal/config.yaml` | pass: all diagnostics true |
| `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json` | pass: delivered dry-run reply |
| Simple secret scan | pass: no common token/private-key patterns found |
| Case-sensitive secret scan after decoupling | pass: no common secret patterns found |
| Generated cache cleanup | pass: `.pytest_cache` and `__pycache__` removed |
| `python -m ruff check .` | pass: all checks passed |
| `python scripts/check_release_ready.py` | pass: release readiness checks passed |
| `python -m build` | pass: sdist and wheel built successfully |
| `python -m twine check dist/*` | pass: wheel and sdist passed |
| Final generated artifact cleanup | pass: `dist`, `build`, egg-info, caches removed |

## Security Review Summary

- No high-confidence vulnerabilities identified in the MVP code.
- WeChat callback verification is implemented for production request validation.
- Real outbound WeChat delivery is intentionally not implemented yet and fails closed unless `dry_run` is enabled.
- Secrets are represented by placeholders only and `.env` is ignored.
- Service APIs require `runtime.service_api_token` when binding to non-loopback hosts; token auth is tested.
- Web UI integration is constrained to service APIs and does not own WeChat runtime logic.
- Open-source hardening adds CI/security/release workflows and community governance assets; public launch still requires replacing repository owner URLs if needed and enabling GitHub repository settings.
- Local build/publish readiness passes after adopting SPDX license metadata and cleaning generated artifacts.

## Skills Trace

- SKILLS_TRACE: using-superpowers -> brainstorming -> planning-with-files -> backend-delivery -> cc-skill-coding-standards -> cc-skill-backend-patterns -> security-review planned for auth/input/sensitive-data surfaces.
- SKILLS_TRACE: repeatable-task-bootstrap -> planning-with-files -> backend-delivery for decoupling execution; RCCP unavailable, fallback evidence recorded in `task_plan.md` and `progress.md`.
