# Failure Modes

```mermaid
flowchart TD
  A["Incoming WeChat Event"] --> B{"Valid Signature?"}
  B -- "No" --> X["Reject + Log"]
  B -- "Yes" --> C{"Duplicate Event?"}
  C -- "Yes" --> Y["Ack Without Reprocessing"]
  C -- "No" --> D{"Hermes Available?"}
  D -- "No" --> E["Send Friendly Failure Message"]
  D -- "Yes" --> F["Run Hermes Session"]
  F --> Q{"Governor Allows?"}
  Q -- "No" --> L["Queue + Friendly Local Status"]
  Q -- "Yes" --> G{"Delivery OK?"}
  G -- "Yes" --> H["Record Delivery Success"]
  G -- "No" --> I["Retry With Backoff"]
  I --> J{"Retry Exhausted?"}
  J -- "No" --> G
  J -- "Yes" --> K["Record Failure + Fallback Notice"]
```

## Friendly Fallbacks

- Invalid signature: reject without user-visible detail.
- Duplicate event: acknowledge without a second Hermes call.
- Hermes timeout: tell the user the agent is busy and suggest retrying later.
- Delivery failure: retry with backoff and record diagnostic context.
- Weixin rate limit: count the failed attempt, open the governor, queue remaining notifications, and wait for the next window.
- Overlong response: split or summarize before sending.
- Governor queued: do not send a WeChat message explaining the limit; expose a friendly card through local/Web UI status and merge queued notifications later.

## Operator Signals

Every failure should provide an operator-facing reason while keeping user-visible replies safe and short.
