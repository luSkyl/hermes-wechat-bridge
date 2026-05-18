# Message Lifecycle

```mermaid
sequenceDiagram
  participant User as WeChat User
  participant WeChat as WeChat Server
  participant Adapter as WeChat Adapter
  participant Gateway as Gateway Runtime
  participant Hermes as Hermes Agent
  participant Delivery as Delivery Layer

  User->>WeChat: Send message
  WeChat->>Adapter: Webhook event
  Adapter->>Adapter: Verify signature
  Adapter->>Gateway: Normalize event
  Gateway->>Gateway: Dedupe + session lookup
  Gateway->>Hermes: Send prompt
  Hermes-->>Gateway: Stream/final response
  Gateway->>Gateway: Format friendly reply
  Gateway->>Delivery: Send response
  Delivery->>WeChat: Deliver message
  WeChat-->>User: Show reply
```

## Event States

1. `received`: raw webhook reached the adapter.
2. `verified`: signature and required fields passed validation.
3. `normalized`: payload became a `MessageEvent`.
4. `routed`: the event was mapped to a Hermes session.
5. `answered`: Hermes returned a response or a safe fallback was generated.
6. `delivered`: outbound message was sent or dry-run emitted.

## Idempotency

The bridge deduplicates by event ID. Replayed webhook events should be acknowledged without invoking Hermes again.
