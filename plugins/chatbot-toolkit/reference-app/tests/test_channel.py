from app.channel import WhatsAppChannel


def make_channel() -> WhatsAppChannel:
    return WhatsAppChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        phone_number_id="PNID",
    )


def test_verify_returns_challenge_on_match():
    channel = make_channel()
    challenge = channel.verify(
        {"hub.mode": "subscribe", "hub.verify_token": "vtok", "hub.challenge": "12345"}
    )
    assert challenge == "12345"


def test_verify_returns_none_on_bad_token():
    channel = make_channel()
    assert (
        channel.verify(
            {"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"}
        )
        is None
    )


import hashlib
import hmac


def sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature_accepted():
    channel = make_channel()
    body = b'{"hello":"world"}'
    headers = {"x-hub-signature-256": sign("shh", body)}
    assert channel.verify_signature(body, headers) is True


def test_invalid_signature_rejected():
    channel = make_channel()
    body = b'{"hello":"world"}'
    headers = {"x-hub-signature-256": "sha256=deadbeef"}
    assert channel.verify_signature(body, headers) is False


def test_missing_signature_rejected():
    channel = make_channel()
    assert channel.verify_signature(b"{}", {}) is False


import json
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_extracts_text_message():
    channel = make_channel()
    body = (FIXTURES / "whatsapp_message.json").read_bytes()
    inbound = channel.parse(body)
    assert inbound is not None
    assert inbound.conversation_id == "15557654321"
    assert inbound.text == "Hello bot"


def test_parse_returns_none_for_status_event():
    channel = make_channel()
    body = (FIXTURES / "whatsapp_status.json").read_bytes()
    assert channel.parse(body) is None


def test_parse_returns_none_for_garbage():
    channel = make_channel()
    assert channel.parse(b"not json") is None


import asyncio

import httpx

from app.models import OutboundMessage


def test_send_posts_to_graph_with_reply():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"messages": [{"id": "wamid.out"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    channel = WhatsAppChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        phone_number_id="PNID",
        client=client,
    )
    asyncio.run(channel.send(OutboundMessage(conversation_id="15557654321", text="hi there")))

    assert captured["url"] == "https://graph.facebook.com/v21.0/PNID/messages"
    assert captured["auth"] == "Bearer atok"
    assert captured["json"] == {
        "messaging_product": "whatsapp",
        "to": "15557654321",
        "type": "text",
        "text": {"body": "hi there"},
    }
