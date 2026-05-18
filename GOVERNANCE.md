# Governance

Hermes WeChat Bridge is maintained as a focused, open-source bridge for one golden path: Hermes Agent to WeChat.

## Maintainer Responsibilities

- Keep Hermes and Hermes Web UI upgradeable by preserving the bridge boundary.
- Protect users from unsafe defaults, secret leakage, and confusing failure modes.
- Review public contracts carefully before accepting breaking changes.
- Keep docs, tests, examples, and release notes aligned with behavior.

## Decision Rules

1. Reliability and safety beat feature breadth.
2. One stable golden path beats many incomplete integrations.
3. Additive changes are preferred over breaking changes.
4. WeChat runtime logic belongs in this repository, not Hermes or Hermes Web UI.
5. Web UI integrations must consume service APIs instead of reimplementing bridge logic.

## Change Classes

| Class | Examples | Requirement |
|---|---|---|
| Patch | docs, tests, small bug fixes | Maintainer review and passing CI |
| Minor | new optional endpoint, new diagnostic | Contract tests and docs update |
| Major | response shape change, config rename | Migration guide, compatibility window, major version bump |
| Security | signature, auth, secret handling | Private report handling and security review |

## Release Authority

Maintainers may publish releases after CI passes, release notes are prepared, and the publication checklist is complete.
