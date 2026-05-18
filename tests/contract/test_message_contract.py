from bridge.protocol import MessageKind
from bridge.runtime.config import WeChatConfig
from bridge.wechat.adapter import WeChatAdapter


def test_text_message_normalizes_to_protocol_event() -> None:
    adapter = WeChatAdapter(WeChatConfig(token="dev-token"))

    event = adapter.normalize(
        {
            "MsgId": "msg-1",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "CreateTime": "1710000000",
            "Content": "hello",
        }
    )

    assert event.event_id == "msg-1"
    assert event.platform == "wechat"
    assert event.conversation_id == "bridge"
    assert event.sender_id == "user-1"
    assert event.kind == MessageKind.TEXT
    assert event.prompt_text() == "hello"


def test_command_message_is_detected() -> None:
    adapter = WeChatAdapter(WeChatConfig(token="dev-token"))

    event = adapter.normalize(
        {
            "MsgId": "msg-2",
            "MsgType": "text",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "Content": "/status",
        }
    )

    assert event.kind == MessageKind.COMMAND


def test_image_message_preserves_attachment() -> None:
    adapter = WeChatAdapter(WeChatConfig(token="dev-token"))

    event = adapter.normalize(
        {
            "MsgId": "msg-3",
            "MsgType": "image",
            "FromUserName": "user-1",
            "ToUserName": "bridge",
            "MediaId": "media-1",
            "PicUrl": "https://example.invalid/image.jpg",
        }
    )

    assert event.kind == MessageKind.IMAGE
    assert event.attachments[0].attachment_id == "media-1"
    assert event.attachments[0].kind == "image"
