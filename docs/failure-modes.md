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
  F --> G{"Delivery OK?"}
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
- Overlong response: split or summarize before sending.

## Operator Signals

Every failure should provide an operator-facing reason while keeping user-visible replies safe and short.
