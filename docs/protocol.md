# Protocol

The bridge protocol keeps platform-specific WeChat payloads away from the runtime. Adapters normalize inbound events into `MessageEvent`, Hermes returns `HermesResponse`, and the delivery layer emits `DeliveryResult`.

## MessageEvent

Required fields:

- `event_id`: stable id used for dedupe.
- `platform`: always `wechat` in the MVP.
- `conversation_id`: WeChat account, room, or callback target id.
- `sender_id`: user id from the inbound event.
- `kind`: `text`, `image`, `file`, `command`, or `unknown`.
- `text`: normalized user-visible text.

See `schemas/message-event.schema.json`.

## DeliveryResult

Required fields:

- `ok`: whether delivery succeeded.
- `delivery_id`: platform or dry-run id when available.
- `error`: safe operator-facing error when delivery fails.
- `attempts`: number of attempts used.

See `schemas/delivery-result.schema.json`.

## Compatibility Rules

- Add fields instead of renaming existing fields.
- Preserve `event_id`, `conversation_id`, `sender_id`, and `kind` semantics.
- Keep user-visible error text safe and short.
- Contract tests should pass before changing runtime behavior.
