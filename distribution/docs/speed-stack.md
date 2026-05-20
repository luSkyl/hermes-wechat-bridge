# Hermes WeChat Speed Stack

The WeChat distribution keeps ordinary chat responsive by applying a small
gateway-side speed router before the full Hermes Agent loop starts.

## Runtime Defaults

Add these keys to `~/.hermes/config.yaml` when you want to tune behavior without
editing code:

```yaml
speed:
  enabled: true
  fast_chat_enabled: true
  fast_chat_for_followups: true
  fast_chat_max_chars: 420
  fast_chat_max_iterations: 4
  fast_chat_reasoning_effort: low
  fast_chat_toolsets: []
  first_ack_enabled: true
  complex_first_ack_seconds: 2
  progress_first_after: 45
```

## Routing Contract

- Ordinary chat, formatting advice, template discussion, and short subjective questions use the fast chat route.
- Emergency/safety messages use a fast safety route with sober tone.
- Code changes, files, GitHub, searches, images, reminders, and troubleshooting stay on the full agent route.
- Full agent tasks send a first acknowledgement after `complex_first_ack_seconds` if they have not already completed.
- Long-running progress uses `progress_first_after` when it is lower than `agent.gateway_notify_interval`.

## User Experience

- Normal answers still render through the friendly ordinary reply card.
- Complex tasks show `🧭 我已接手这件事` before the longer execution path becomes visible.
- WeChat remains low-noise: the fast route does not send progress cards, and the full route sends only useful staged status.
