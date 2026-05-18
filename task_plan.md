
## Hermes Native Integration Kit Closeout Plan

Started: 2026-05-18 19:30:50 +08:00

Goal: make hermes-wechat-bridge a single-repo, cloneable, governed WeChat notification runtime with Hermes native integration shims.

Phases:
1. Baseline probe and ownership: complete
2. Integration kit implementation: complete
3. Examples/docs/tests: complete
4. Validation gates: complete
5. Commit and push: complete

Acceptance gates:
- python -m py_compile for touched bridge modules passes.
- python -m ruff check bridge tests passes.
- python -m pytest tests -q passes.
- CLI smoke for 
otify, lush, erify-hermes-native passes.
- No raw Traceback, et=-2, errcode=-2 in user-visible friendly cards.

RCCP: scripts/rccp/rccp.ps1 is absent in this repository, so task-start/resume/ownership gates are degraded to this file plan plus pytest/ruff/compile evidence.



