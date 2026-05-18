# Support

## Where to Ask

- Use GitHub Discussions or issues for public questions once the repository is published.
- Use `SECURITY.md` for vulnerabilities or accidental secret exposure.
- Include sanitized configs and simulator output when asking for help.

## What to Include

- Bridge version or commit SHA.
- Python version and operating system.
- Hermes connection mode: `mock`, `http`, or other adapter.
- Whether WeChat delivery is `dry_run` or real.
- Output from `python -m bridge.cli doctor --config <path>`.
- A sanitized event payload or simulator fixture.

## Not Supported

- Debugging private credentials posted publicly.
- Using the bridge for spam, abuse, or policy-violating automation.
- Maintaining forks that mix WeChat runtime logic back into Hermes or Hermes Web UI.
