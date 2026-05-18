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
  Gateway->>Delivery: Reserve governor quota
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
6. `admitted`: the Weixin Delivery Governor reserved a send attempt or queued the message.
7. `delivered`: outbound message was sent or dry-run emitted.

## Idempotency

The bridge deduplicates by event ID. Replayed webhook events should be acknowledged without invoking Hermes again.

## Delivery Governance

The Weixin Delivery Governor sits below friendly reply formatting and above the actual sender. It learns a safe per-window send budget, counts failed attempts, opens a circuit after `ret=-2`/`errcode=-2`, and releases queued messages by priority in later windows. Low-priority queued notices expire first so stale background alerts do not crowd out fresh user-facing updates.

## Runtime Notifications

Cron failures, Guardian incidents, and direct operational notifications enter through `BridgeNotifier` or the specific Cron/Guardian adapters. The adapters first render a friendly card, then pass the card through the governor. If the governor queues the message, callers receive a local/Web UI friendly status instead of sending a second WeChat message about WeChat being rate limited.
