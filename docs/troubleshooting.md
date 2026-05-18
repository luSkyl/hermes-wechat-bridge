# Troubleshooting

## `doctor` Fails

- Check the config path.
- Confirm required sections: `bridge`, `wechat`, `hermes`, and `runtime`.
- Ensure `wechat.token` is not empty.

## Simulator Returns Duplicate

The dedupe store saw the same event ID twice. Change `event_id` in the sample event or wait for TTL expiry.

## Hermes Does Not Respond

- In mock mode, verify the config has `hermes.mode: mock`.
- In HTTP mode, confirm `hermes.endpoint` is reachable from the bridge host.
- Check timeout settings.

## Real WeChat Callback Fails

- Verify timestamp, nonce, and signature inputs.
- Ensure the callback token exactly matches your bridge config.
- Confirm the public callback URL points to the bridge and uses HTTPS.

## Replies Are Too Long

The formatter applies a max length. Tune the limit or add summarization in the Hermes side.
