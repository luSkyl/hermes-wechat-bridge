# Security Model

## Trust Boundaries

- WeChat webhook traffic is untrusted until signature verification succeeds.
- User text, file names, media IDs, and command-like content are untrusted input.
- Hermes responses may include sensitive local context and must be formatted before display.

## Required Controls

- Verify webhook signatures for production traffic.
- Protect service APIs with `runtime.service_api_token` when binding outside localhost.
- Keep secrets outside git.
- Redact tokens, local paths, stack traces, and private config from user-visible replies.
- Reject malformed events before routing to Hermes.
- Avoid shell execution from chat input.

## Logging

Logs should include event IDs and high-level failure reasons. Logs should not include access tokens, app secrets, raw credentials, or private message content unless explicitly enabled in a secure environment.

## Incident Response

If a secret is committed or logged, rotate it immediately, remove it from public history where possible, and document the exposure window.
