---
name: testing-bots
description: Test a Meta messaging bot in the chatbot-toolkit stack without live services — simulate webhook payloads from captured fixtures, sign them like Meta does, mock the Graph and Anthropic APIs, and assert behavior through public interfaces. Use when writing tests for a bot, simulating a webhook, faking an inbound WhatsApp/Instagram message, mocking the Graph or Anthropic API, testing the brain or guardrails, or asking how the reference app tests itself.
---

# Testing a Bot

The reference app is built so every test runs offline: no Meta webhook, no Graph
call, no Anthropic call, no real Postgres reach-out. That works because the bot is
assembled from injectable seams and the only two outbound network boundaries —
**Graph** and **Anthropic** — are mockable. Test through those seams, not around
them. The runner is plain `pytest` with `asyncio.run` (no `pytest-asyncio`).

## The seams

`create_app` is a factory that takes every collaborator as an argument, so a test
wires the exact doubles it needs (`reference-app/app/webhook.py`):

    app = create_app(
        channel=channel,                  # real WhatsAppChannel, fake Graph client
        brain=StubBrain("Hello Ada!"),    # canned reply, no Anthropic call
        store=InMemorySessionStore(),     # swap for PostgresSessionStore in prod
        guardrails=NoOpGuardrails(),      # or HeuristicGuardrails to test screening
    )

- **`SessionStore`** — `InMemorySessionStore` is the test double for the Postgres
  store; same `append`/`get_history` interface, no database. See `bot-session-state`.
- **`Channel`** — real `WhatsAppChannel`, but its `httpx` client is injected, so
  Graph never gets hit (below). See `meta-messaging`.
- **`Brain`** — a tiny class with `async def respond(...)` stands in for Claude. See
  `bot-brain-basics`.
- **`Guardrails`** — deterministic and network-free, so it's real in every test. See
  `bot-safety`.

## Integration over unit (the house default)

The preferred test is the **webhook integration test**: drive the whole flow
(verify signature → load history → brain → screen → append → send) through the HTTP
boundary with FastAPI's `TestClient`, mocking only Graph and Anthropic. One test
covers wiring that a pile of unit tests would miss
(`reference-app/tests/test_webhook_integration.py`):

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

Assert on what crossed a public boundary — the HTTP status and the JSON Graph
received — never on private attributes.

## Simulating webhook payloads

Inbound payloads are **captured fixtures**, checked in under `tests/fixtures/`
(`whatsapp_message.json`, `whatsapp_status.json`). Read the raw bytes and post them
verbatim — don't hand-build dicts, because the bot verifies the signature over the
exact bytes Meta sent. To add a channel or message type, capture a real payload once
and save it as a new fixture.

Meta signs every POST with `X-Hub-Signature-256`. Reproduce that signature in tests
with the same HMAC the app verifies (`reference-app/tests/test_channel.py`):

    def sign(secret: str, body: bytes) -> str:
        return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

A signed body exercises the accept path; a bad `sha256=…` header exercises rejection
— and a good rejection test proves the brain was **never reached**:

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

## Mocking Graph (outbound)

`WhatsAppChannel.send` posts to Graph through an injected `httpx.AsyncClient`. Give
it `httpx.MockTransport(handler)` and the handler both **captures** what was sent and
**returns** a canned Graph response — letting you assert the URL, the `Bearer` auth
header, and the exact JSON body without a network call (`test_channel.py`).

## Mocking Anthropic (the brain)

Two levels, depending on what you're testing:

- **Don't care how the reply is produced** → inject a `StubBrain` with a canned
  `respond()` (most webhook/flow tests).
- **Testing `ClaudeBrain` itself** → inject a fake Anthropic client and assert the
  request shape — that history is mapped to `messages` in order and the right `model`
  is sent (`reference-app/tests/test_brain.py`):

      class FakeMessages:
          def __init__(self, reply_text):
              self._reply_text = reply_text
              self.calls = []
          async def create(self, **kwargs):
              self.calls.append(kwargs)
              return SimpleNamespace(content=[SimpleNamespace(type="text", text=self._reply_text)])

      class FakeAnthropic:
          def __init__(self, reply_text):
              self.messages = FakeMessages(reply_text)

## Async without pytest-asyncio

Every collaborator is `async`, but the tests stay plain functions. Call an async
method with `asyncio.run(...)`; the FastAPI `TestClient` runs the event loop for HTTP
tests itself. This keeps the suite dependency-light — see `test_session.py` and
`test_channel.py` for the `asyncio.run` pattern.

## Postgres: a real temp database

The one seam worth testing against the real thing is the Postgres store. Use
**`pytest-postgresql`**, which spins up a throwaway database per test and hands you a
fixture; build the store from its DSN and run the same `append`/`get_history`
assertions as the in-memory store (`reference-app/tests/test_postgres_session.py`).
Identical assertions across both stores prove they're interchangeable.

## Running the suite

    cd plugins/chatbot-toolkit/reference-app
    uv run pytest

Fast, offline, deterministic. If a test needs a live token or a real Graph call to
pass, the seam is in the wrong place — push the boundary out and mock it.
