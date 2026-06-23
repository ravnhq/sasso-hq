import asyncio
import hashlib
import hmac
import json
from pathlib import Path

import httpx

from app.channel import InstagramChannel
from app.models import OutboundMessage

FIXTURES = Path(__file__).parent / "fixtures"


def make_channel() -> InstagramChannel:
    return InstagramChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        ig_id="IGID",
    )


def sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_verify_returns_challenge_on_match():
    challenge = make_channel().verify(
        {"hub.mode": "subscribe", "hub.verify_token": "vtok", "hub.challenge": "12345"}
    )
    assert challenge == "12345"


def test_verify_returns_none_on_bad_token():
    assert (
        make_channel().verify(
            {"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"}
        )
        is None
    )


def test_valid_signature_accepted():
    body = b'{"hello":"world"}'
    headers = {"x-hub-signature-256": sign("shh", body)}
    assert make_channel().verify_signature(body, headers) is True


def test_invalid_signature_rejected():
    body = b'{"hello":"world"}'
    headers = {"x-hub-signature-256": "sha256=deadbeef"}
    assert make_channel().verify_signature(body, headers) is False


def test_missing_signature_rejected():
    assert make_channel().verify_signature(b"{}", {}) is False


def test_parse_extracts_text_dm():
    body = (FIXTURES / "instagram_message.json").read_bytes()
    inbound = make_channel().parse(body)
    assert inbound is not None
    assert inbound.conversation_id == "1089304999999999"
    assert inbound.text == "Hello bot"


def test_parse_ignores_echo():
    body = (FIXTURES / "instagram_echo.json").read_bytes()
    assert make_channel().parse(body) is None


def test_parse_returns_none_for_garbage():
    assert make_channel().parse(b"not json") is None


def test_send_posts_to_graph_with_reply():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"recipient_id": "1089304999999999", "message_id": "mid.out"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    channel = InstagramChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        ig_id="IGID",
        client=client,
    )
    asyncio.run(
        channel.send(OutboundMessage(conversation_id="1089304999999999", text="hi there"))
    )

    assert captured["url"] == "https://graph.facebook.com/v21.0/IGID/messages"
    assert captured["auth"] == "Bearer atok"
    assert captured["json"] == {
        "recipient": {"id": "1089304999999999"},
        "message": {"text": "hi there"},
    }
