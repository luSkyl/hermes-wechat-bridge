# Security Policy

Hermes WeChat Bridge sits between a chat platform and an agent runtime. Treat all inbound messages, attachments, and webhook metadata as untrusted input.

## Reporting Vulnerabilities

Please report vulnerabilities privately through the repository Security tab after publication, or contact the maintainers privately. Do not open public issues for exploitable bugs involving secrets, authentication bypass, webhook spoofing, message injection, or unintended file access.

## Supported Versions

| Version | Supported |
|---|---|
| `main` | Security fixes before first public release |
| `0.1.x` | Supported after initial public release |

## Security Boundaries

- WeChat webhook signatures must be verified before processing production traffic.
- Secrets must live in environment variables or local config files excluded by `.gitignore`.
- The bridge should not expose arbitrary local file reads to chat users.
- User-visible errors should be friendly but should not reveal tokens, stack traces, local paths, or private configuration.

## Production Recommendations

- Use HTTPS for public callbacks.
- Use a long random WeChat token.
- Restrict bridge network access to the minimum required endpoints.
- Rotate credentials after accidental exposure.
- Keep logs redacted and retention-limited.

## Disclosure Expectations

Maintainers aim to acknowledge valid private reports promptly, reproduce the issue, prepare a fix, and publish a security advisory or release note when appropriate.
