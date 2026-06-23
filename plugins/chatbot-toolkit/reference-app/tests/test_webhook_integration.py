from fastapi.testclient import TestClient

from app.channel import InstagramChannel, WhatsAppChannel
from app.guardrails import NoOpGuardrails
from app.session import InMemorySessionStore
from app.webhook import create_app


class StubBrain:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    async def respond(self, history, incoming):
        return self.reply


def build_client(channel: WhatsAppChannel, brain) -> TestClient:
    app = create_app(
        channel=channel,
        brain=brain,
        store=InMemorySessionStore(),
        guardrails=NoOpGuardrails(),
    )
    return TestClient(app)


def make_channel(client=None) -> WhatsAppChannel:
    return WhatsAppChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        phone_number_id="PNID",
        client=client,
    )


def test_get_webhook_returns_challenge():
    client = build_client(make_channel(), StubBrain("x"))
    resp = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "vtok", "hub.challenge": "99"},
    )
    assert resp.status_code == 200
    assert resp.text == "99"


def test_get_webhook_rejects_bad_token():
    client = build_client(make_channel(), StubBrain("x"))
    resp = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "99"},
    )
    assert resp.status_code == 403


import hashlib
import hmac
import json
from pathlib import Path

import httpx

FIXTURES = Path(__file__).parent / "fixtures"


def sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_post_webhook_replies_via_graph():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"messages": [{"id": "wamid.out"}]})

    graph_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    channel = make_channel(client=graph_client)
    client = build_client(channel, StubBrain("Hello Ada!"))

    body = (FIXTURES / "whatsapp_message.json").read_bytes()
    resp = client.post(
        "/webhook",
        content=body,
        headers={"x-hub-signature-256": sign("shh", body)},
    )

    assert resp.status_code == 200
    assert captured["json"]["to"] == "15557654321"
    assert captured["json"]["text"]["body"] == "Hello Ada!"


def test_post_webhook_routes_instagram_through_same_flow():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"recipient_id": "1089304999999999", "message_id": "mid.out"})

    graph_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    channel = InstagramChannel(
        app_secret="shh",
        verify_token="vtok",
        access_token="atok",
        ig_id="IGID",
        client=graph_client,
    )
    client = build_client(channel, StubBrain("Hello Ada!"))

    body = (FIXTURES / "instagram_message.json").read_bytes()
    resp = client.post(
        "/webhook",
        content=body,
        headers={"x-hub-signature-256": sign("shh", body)},
    )

    assert resp.status_code == 200
    assert captured["url"] == "https://graph.facebook.com/v21.0/IGID/messages"
    assert captured["json"] == {
        "recipient": {"id": "1089304999999999"},
        "message": {"text": "Hello Ada!"},
    }


def test_get_privacy_policy_page():
    client = build_client(make_channel(), StubBrain("x"))
    resp = client.get("/privacy")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "privacy" in resp.text.lower()


def test_get_data_deletion_page():
    client = build_client(make_channel(), StubBrain("x"))
    resp = client.get("/data-deletion")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "delet" in resp.text.lower()


def test_post_webhook_rejects_bad_signature():
    called = {"brain": False}

    class SpyBrain:
        async def respond(self, history, incoming):
            called["brain"] = True
            return "x"

    client = build_client(make_channel(), SpyBrain())
    body = (FIXTURES / "whatsapp_message.json").read_bytes()
    resp = client.post(
        "/webhook", content=body, headers={"x-hub-signature-256": "sha256=bad"}
    )

    assert resp.status_code == 403
    assert called["brain"] is False
