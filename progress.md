# Progress: Hermes WeChat Bridge

## Session Log

- Started project scaffold for a new open-source Hermes to WeChat golden path.
- Created file-based planning artifacts before implementation.
- SKILLS_TRACE: using-superpowers -> brainstorming -> planning-with-files -> backend-delivery -> cc-skill-coding-standards -> cc-skill-backend-patterns -> security-review planned.
- Added project metadata, README, security/contribution docs, and gateway architecture documentation with Mermaid diagrams.
- Implemented protocol models, config loading, WeChat adapter/verifier/formatter/sender, Hermes client, router, dedupe, retry, diagnostics, and CLI commands.
- Added simulator, sample WeChat events, minimal run scripts, and Docker Compose demo configuration.
- Added protocol schemas, callback server, WeChat XML helpers, and contract/integration tests.
- Ran verification and cleaned generated caches.
- Started decoupling execution to keep Hermes and Hermes Web UI upgradeable while moving WeChat chain ownership into this bridge.
- SKILLS_TRACE: repeatable-task-bootstrap -> planning-with-files -> backend-delivery; RCCP unavailable, using local planning files as fallback evidence.
- Added sync strategy, compatibility matrix, migration map, and upgrade playbook to document three-project decoupling boundaries.
- Added stable Bridge service/API surface for health, status, simulation, and direct session-message delivery.
- Added Hermes contract tests, Bridge service tests, HTTP service API tests, and service API token protection for non-loopback serving.
- Ran full verification after decoupling and cleaned generated caches.
- Added open-source launch assets: code of conduct, governance, maintainers, support, roadmap, changelog, release process, issue forms, PR template, Dependabot, CI, CodeQL, dependency review, Scorecard, labeler, release workflow, and release-ready script.
- Added packaging metadata, ruff lint config, release readiness checks, launch checklist, maintainer guide, and README badges/community links.
- Verified lint, tests, compile, CLI smoke, release readiness, package build, and package metadata checks; cleaned generated artifacts.
- SKILLS_TRACE: using-superpowers -> brainstorming -> planning-with-files -> backend-delivery -> governance-neat-check -> cc-skill-coding-standards -> security-review.
- Upgraded public launch surface after first alpha: README positioning, release-note categories, PyPI trusted-publishing gated workflow, release process docs, and launch checklist status.
- Added Weixin Delivery Governor as the outbound send-attempt budget, queue, breaker, and friendly-card layer for alpha.3.

## Commands and Evidence

| Command | Result | Evidence |
|---|---|---|
| `New-Item -ItemType Directory -Force hermes-wechat-bridge` | pass | Project directory created |
| `apply_patch` docs and metadata | pass | README, docs, pyproject, license, examples baseline files created |
| `apply_patch` runtime modules | pass | Core bridge runtime and CLI created |
| `apply_patch` simulator/examples | pass | Local simulator and example configs/scripts created |
| `python -m pytest` | pass | 13 passed |
| `python -m bridge.cli --help` | pass | doctor/simulate/serve commands available |
| `python -m bridge.cli doctor --config examples/minimal/config.yaml` | pass | diagnostics ok |
| `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json` | pass | dry-run delivery returned ok |
| simple secret scan | pass | no common secret patterns found |
| RCCP task-start | degraded | `scripts/rccp/rccp.ps1` not present in this new project; fallback to project planning files |
| `apply_patch` decoupling docs | pass | `docs/sync-strategy.md`, `docs/compatibility-matrix.md`, `docs/migration-map.md`, `docs/upgrade-playbook.md` |
| `apply_patch` stable service API | pass | `bridge/server.py`, `bridge/runtime/service.py` |
| `python -m pytest` | failed then fixed | HTTP session-message endpoint returned `name 'sender' is not defined`; fixed server closure |
| `python -m pytest` after service API auth | pass | 21 passed |
| `python -m bridge.cli doctor --config examples/minimal/config.yaml` | pass | diagnostics ok after service API auth |
| `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json` | pass | dry-run delivery ok after service API auth |
| case-sensitive secret scan | pass | no common secret patterns found |
| cache cleanup | pass | `.pytest_cache` and `__pycache__` removed |
| `apply_patch` open-source hardening | pass | community files, `.github` workflows/templates, `scripts/check_release_ready.py`, launch docs |
| `python -m ruff check .` | pass | all checks passed |
| `python scripts/check_release_ready.py` | pass | tests, compile, doctor, simulate, secret scan passed |
| `python -m build` | pass | sdist and wheel built |
| `python -m twine check dist/*` | pass | package metadata checks passed |
| generated artifact cleanup | pass | removed `dist`, `build`, egg-info, `.pytest_cache`, `.ruff_cache`, `__pycache__` |
| GitHub Actions after alpha release | pass | CI, CodeQL, Scorecard, and Release succeeded on `main`/`v0.1.0-alpha.1` |
| Public release verification | pass | `v0.1.0-alpha.1` prerelease has wheel and sdist assets |

## Verification

- Complete: pytest, CLI doctor, CLI simulator, secret scan, cache cleanup.

[2026-05-18 17:50:16 +08:00] Added Weixin Delivery Governor, config knobs, sender integration, docs, and contract tests.

[2026-05-18 19:03:28 +08:00] Runtime notification completeness: added friendly-card templates, BridgeNotifier, CronDeliveryNotifier, GuardianDeliveryNotifier, CLI notify/flush, sender transport + queued flush support, and contract tests so open-source users get the same governed notification behavior as local Hermes deployments. Validation: py_compile passed; ruff check bridge tests passed; pytest tests passed (32 passed); CLI notify/flush smoke passed in dry-run mode.
