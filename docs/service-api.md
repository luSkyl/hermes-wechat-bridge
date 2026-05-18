# Service API

The service API lets Hermes Web UI and operators observe or test the bridge without taking ownership of WeChat runtime logic.

By default the CLI binds to `127.0.0.1`. If you serve on a non-loopback host, configure `runtime.service_api_token`; service API requests must then include either `Authorization: Bearer <token>` or `X-Bridge-Token: <token>`.

## `GET /health`

Returns diagnostics suitable for readiness checks.

```json
{
  "ok": true,
  "checks": {
    "bridge_name": true,
    "wechat_token": true,
    "hermes_mode": true,
    "hermes_endpoint": true,
    "retry_attempts": true,
    "dedupe_ttl": true
  },
  "messages": []
}
```

## `GET /status`

Returns safe runtime metadata. This endpoint must not expose tokens, private chat IDs, or message content.

## `GET /delivery/status`

Returns safe Weixin Delivery Governor state for local dashboards and Web UI panels. It exposes queue size, current circuit state, window capacity, remaining attempts, and next available time without exposing raw chat IDs or secrets.

## `POST /notify`

Sends or queues an operational notification. Body:

```json
{
  "target_id": "wxid_home",
  "title": "上游模型已恢复",
  "text": "模型恢复后需要重新执行定时任务。",
  "priority": "high"
}
```

The service wraps `text` in the friendly-card template before it reaches WeChat and admits the attempt through the governor.

## `POST /flush`

Attempts to flush queued notifications for a target. Body:

```json
{
  "target_id": "wxid_home",
  "limit": 3
}
```

Flush volume is still governed by the current send window, so releasing queued cards cannot bypass the iLink protection circuit.

## `POST /simulate`

Replays a WeChat-like JSON event through the bridge. This is intended for diagnostics, local development, and Web UI smoke checks.

## `POST /sessions/{id}/message`

Sends a controlled direct message through the bridge delivery layer. The session id format is `platform:conversation:sender`.

## Web UI Rule

Hermes Web UI may consume these endpoints for observation and diagnostics. It must not reimplement callback handling, dedupe, retry, session mapping, friendly-card rendering, or delivery governance.
