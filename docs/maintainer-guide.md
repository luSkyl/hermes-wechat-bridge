# Maintainer Guide

## Triage Labels

- `bug`: reproducible incorrect behavior.
- `enhancement`: scoped improvement request.
- `wechat`: WeChat callback, parsing, delivery, or setup.
- `runtime`: session, dedupe, retry, router, diagnostics.
- `documentation`: docs, examples, or copy.
- `security`: private handling preferred for exploitable issues.
- `needs-triage`: issue requires maintainer review.

## Review Priorities

1. Safety and secret handling.
2. Compatibility with Hermes and Hermes Web UI boundaries.
3. Reproducible tests and simulator fixtures.
4. Clear docs and migration notes.
5. Minimality and maintainability.

## Release Notes

Every release should mention:

- User-visible behavior changes.
- Compatibility impacts.
- Security hardening.
- Migration steps if any.
- Known limitations.
