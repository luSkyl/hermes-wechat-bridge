from bridge.wechat.xml import parse_wechat_xml, render_text_reply


def test_parse_wechat_xml_payload() -> None:
    payload = parse_wechat_xml(
        "<xml>"
        "<ToUserName><![CDATA[bridge]]></ToUserName>"
        "<FromUserName><![CDATA[user-1]]></FromUserName>"
        "<MsgType><![CDATA[text]]></MsgType>"
        "<Content><![CDATA[hello]]></Content>"
        "</xml>"
    )

    assert payload["ToUserName"] == "bridge"
    assert payload["FromUserName"] == "user-1"
    assert payload["Content"] == "hello"


def test_render_text_reply_swaps_sender_and_recipient() -> None:
    xml = render_text_reply(to_user="user-1", from_user="bridge", content="hello")

    assert "<ToUserName><![CDATA[user-1]]></ToUserName>" in xml
    assert "<FromUserName><![CDATA[bridge]]></FromUserName>" in xml
    assert "<Content><![CDATA[hello]]></Content>" in xml
