# chatbot-toolkit Tracer Bullet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an installable `chatbot-toolkit` plugin whose bundled reference app turns a simulated WhatsApp webhook into a Claude-generated reply, end to end, with a green integration test.

**Architecture:** A new optional marketplace plugin `chatbot-toolkit` containing one runnable FastAPI reference app. The app is built from four deep modules behind simple interfaces — `Channel` (WhatsApp: verify / verify_signature / parse / send), `Brain` (Claude reply), `SessionStore` (conversation history), `Guardrails` (input/output screening) — wired by a deliberately thin webhook layer (`parse → guard → load → brain → append → send`). The app is assembled by a `create_app(channel, brain, store, guardrails)` factory so tests inject fakes/mocks. This slice uses an in-memory `SessionStore` and a no-op `Guardrails` as real seams that slices #3 and #4 fill in.

**Brain note (deviation from PRD, intentional):** the PRD names the Claude Agent SDK for the brain. This tracer bullet implements `Brain` on the raw Anthropic Messages API (`anthropic` package) behind the `respond()` interface — simplest correct, trivially mockable. Slice #6 (`bot-brain-agent`) layers the Agent SDK in without changing the interface.

**Tech Stack:** Python ≥3.12, `uv`, FastAPI + Starlette TestClient, `httpx` (Graph calls + `MockTransport` in tests), `anthropic` SDK, `pytest`. Tests use `asyncio.run(...)` for async units — no extra pytest plugins.

---

## File Structure

```
plugins/chatbot-toolkit/
├── .claude-plugin/plugin.json          # plugin manifest (no version)
├── skills/scaffold-bot/SKILL.md        # the scaffold-bot skill
└── reference-app/
    ├── pyproject.toml                  # uv-managed deps
    ├── .env.example                    # required env vars
    ├── README.md                       # run instructions
    ├── app/
    │   ├── __init__.py
    │   ├── config.py                   # Settings + load_settings()
    │   ├── models.py                   # InboundMessage / OutboundMessage / Message
    │   ├── session.py                  # SessionStore Protocol + InMemorySessionStore
    │   ├── guardrails.py               # Guardrails Protocol + GuardResult + NoOpGuardrails
    │   ├── channel.py                  # Channel Protocol + WhatsAppChannel
    │   ├── brain.py                    # Brain Protocol + ClaudeBrain
    │   ├── webhook.py                  # create_app(...) factory + routes
    │   └── main.py                     # create_default_app() for uvicorn --factory
    └── tests/
        ├── fixtures/whatsapp_message.json
        ├── fixtures/whatsapp_status.json
        ├── test_session.py
        ├── test_channel.py
        ├── test_brain.py
        └── test_webhook_integration.py
```

Top-level repo files touched: `.claude-plugin/marketplace.json`, `plugins/hq-core/taxonomy.yml`, `plugins/hq-core/catalog.json` (regenerated), `CHANGELOG.md`.

---

## Task 0: Branch

- [ ] **Step 1: Create the feature branch**

Run:
```bash
cd /Users/pedrosasso/repos/pedrosasso2/hq
git checkout -b feat/chatbot-toolkit-tracer-bullet
```
Expected: `Switched to a new branch 'feat/chatbot-toolkit-tracer-bullet'`

---

## Task 1: Plugin manifest, marketplace entry, reference-app skeleton

**Files:**
- Create: `plugins/chatbot-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Create: `plugins/chatbot-toolkit/reference-app/pyproject.toml`
- Create: `plugins/chatbot-toolkit/reference-app/app/__init__.py` (empty)
- Create: `plugins/chatbot-toolkit/reference-app/.env.example`

- [ ] **Step 1: Write the plugin manifest**

`plugins/chatbot-toolkit/.claude-plugin/plugin.json`:
```json
{
  "name": "chatbot-toolkit",
  "description": "Optional: build a full-stack, Claude-powered Meta messaging bot (WhatsApp + Instagram) — brain, channels, session state, safety, and deploy.",
  "author": {
    "name": "HQ Core Team",
    "email": "raphaelsasso@ravn.co"
  }
}
```

- [ ] **Step 2: Add the plugin to the marketplace**

In `.claude-plugin/marketplace.json`, add this object to the `plugins` array (after the `fun` entry):
```json
    {
      "name": "chatbot-toolkit",
      "source": "./plugins/chatbot-toolkit",
      "description": "Optional: build a full-stack, Claude-powered Meta messaging bot (WhatsApp + Instagram)."
    }
```
(Add a comma after the preceding `}` so the JSON stays valid.)

- [ ] **Step 3: Write the reference-app pyproject**

`plugins/chatbot-toolkit/reference-app/pyproject.toml`:
```toml
[project]
name = "chatbot-reference-app"
version = "0.1.0"
description = "Reference WhatsApp/Instagram Claude bot for chatbot-toolkit"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "anthropic>=0.40",
]

[dependency-groups]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]
```

- [ ] **Step 4: Write `.env.example`**

`plugins/chatbot-toolkit/reference-app/.env.example`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6
META_APP_SECRET=your-meta-app-secret
META_VERIFY_TOKEN=choose-a-random-verify-token
WHATSAPP_ACCESS_TOKEN=your-whatsapp-cloud-api-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
```

- [ ] **Step 5: Create the package marker**

Create empty file `plugins/chatbot-toolkit/reference-app/app/__init__.py`.

- [ ] **Step 6: Verify manifests parse and deps resolve**

Run:
```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); json.load(open('plugins/chatbot-toolkit/.claude-plugin/plugin.json')); print('json ok')"
cd plugins/chatbot-toolkit/reference-app && uv sync && cd -
```
Expected: `json ok`, then `uv sync` resolves and creates `.venv` without error.

- [ ] **Step 7: Commit**

```bash
git add plugins/chatbot-toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/chatbot-toolkit/reference-app/pyproject.toml plugins/chatbot-toolkit/reference-app/.env.example plugins/chatbot-toolkit/reference-app/app/__init__.py
git commit -m "feat(chatbot): scaffold chatbot-toolkit plugin + reference-app"
```

---

## Task 2: Domain models

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/models.py`

- [ ] **Step 1: Write the models**

`app/models.py`:
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class InboundMessage:
    conversation_id: str
    text: str


@dataclass(frozen=True)
class OutboundMessage:
    conversation_id: str
    text: str


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "assistant"
    text: str
```

- [ ] **Step 2: Verify it imports**

Run:
```bash
cd plugins/chatbot-toolkit/reference-app && uv run python -c "from app.models import InboundMessage, OutboundMessage, Message; print('ok')" && cd -
```
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/models.py
git commit -m "feat(chatbot): add domain message models"
```

---

## Task 3: SessionStore (in-memory)

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/session.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_session.py`

- [ ] **Step 1: Write the failing test**

`tests/test_session.py`:
```python
import asyncio

from app.models import Message
from app.session import InMemorySessionStore


def test_append_then_get_preserves_order():
    store = InMemorySessionStore()
    asyncio.run(store.append("c1", Message(role="user", text="hi")))
    asyncio.run(store.append("c1", Message(role="assistant", text="hello")))
    history = asyncio.run(store.get_history("c1"))
    assert history == [
        Message(role="user", text="hi"),
        Message(role="assistant", text="hello"),
    ]


def test_conversations_are_isolated():
    store = InMemorySessionStore()
    asyncio.run(store.append("c1", Message(role="user", text="a")))
    assert asyncio.run(store.get_history("c2")) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_session.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.session'`

- [ ] **Step 3: Write minimal implementation**

`app/session.py`:
```python
from typing import Protocol

from app.models import Message


class SessionStore(Protocol):
    async def get_history(self, conversation_id: str) -> list[Message]: ...
    async def append(self, conversation_id: str, message: Message) -> None: ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._data: dict[str, list[Message]] = {}

    async def get_history(self, conversation_id: str) -> list[Message]:
        return list(self._data.get(conversation_id, []))

    async def append(self, conversation_id: str, message: Message) -> None:
        self._data.setdefault(conversation_id, []).append(message)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_session.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/session.py plugins/chatbot-toolkit/reference-app/tests/test_session.py
git commit -m "feat(chatbot): add SessionStore protocol + in-memory impl"
```

---

## Task 4: Guardrails (no-op seam)

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/guardrails.py`

- [ ] **Step 1: Write the implementation**

`app/guardrails.py`:
```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    text: str  # possibly-redacted text, or a safe response when blocked


class Guardrails(Protocol):
    def screen_input(self, text: str) -> GuardResult: ...
    def screen_output(self, text: str) -> GuardResult: ...


class NoOpGuardrails:
    """Pass-through seam. Slice #4 (bot-safety) replaces this with real screening."""

    def screen_input(self, text: str) -> GuardResult:
        return GuardResult(allowed=True, text=text)

    def screen_output(self, text: str) -> GuardResult:
        return GuardResult(allowed=True, text=text)
```

- [ ] **Step 2: Verify it imports**

Run:
```bash
cd plugins/chatbot-toolkit/reference-app && uv run python -c "from app.guardrails import NoOpGuardrails, GuardResult; print(NoOpGuardrails().screen_input('x'))" && cd -
```
Expected: `GuardResult(allowed=True, text='x')`

- [ ] **Step 3: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/guardrails.py
git commit -m "feat(chatbot): add Guardrails protocol + no-op seam"
```

---

## Task 5: WhatsAppChannel — verify handshake

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/channel.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_channel.py`

- [ ] **Step 1: Write the failing test**

`tests/test_channel.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.channel'`

- [ ] **Step 3: Write minimal implementation**

`app/channel.py`:
```python
import hashlib
import hmac
import json
from typing import Mapping, Protocol

import httpx

from app.models import InboundMessage, OutboundMessage


class Channel(Protocol):
    def verify(self, params: Mapping[str, str]) -> str | None: ...
    def verify_signature(self, raw_body: bytes, headers: Mapping[str, str]) -> bool: ...
    def parse(self, raw_body: bytes) -> InboundMessage | None: ...
    async def send(self, message: OutboundMessage) -> None: ...


class WhatsAppChannel:
    name = "whatsapp"

    def __init__(
        self,
        app_secret: str,
        verify_token: str,
        access_token: str,
        phone_number_id: str,
        graph_url: str = "https://graph.facebook.com/v21.0",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._app_secret = app_secret
        self._verify_token = verify_token
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._graph_url = graph_url
        self._client = client

    def verify(self, params: Mapping[str, str]) -> str | None:
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == self._verify_token
        ):
            return params.get("hub.challenge")
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/channel.py plugins/chatbot-toolkit/reference-app/tests/test_channel.py
git commit -m "feat(chatbot): add WhatsAppChannel webhook verify handshake"
```

---

## Task 6: WhatsAppChannel — signature validation

**Files:**
- Modify: `plugins/chatbot-toolkit/reference-app/app/channel.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_channel.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_channel.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -k signature -v`
Expected: FAIL with `AttributeError: 'WhatsAppChannel' object has no attribute 'verify_signature'`

- [ ] **Step 3: Write minimal implementation**

Add this method to `WhatsAppChannel` in `app/channel.py`:
```python
    def verify_signature(self, raw_body: bytes, headers: Mapping[str, str]) -> bool:
        provided = headers.get("x-hub-signature-256")
        if not provided:
            return False
        expected = (
            "sha256="
            + hmac.new(self._app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
        )
        return hmac.compare_digest(provided, expected)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/channel.py plugins/chatbot-toolkit/reference-app/tests/test_channel.py
git commit -m "feat(chatbot): validate X-Hub-Signature-256 on inbound webhooks"
```

---

## Task 7: WhatsAppChannel — parse inbound payloads

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/tests/fixtures/whatsapp_message.json`
- Create: `plugins/chatbot-toolkit/reference-app/tests/fixtures/whatsapp_status.json`
- Modify: `plugins/chatbot-toolkit/reference-app/app/channel.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_channel.py`

- [ ] **Step 1: Write the fixtures**

`tests/fixtures/whatsapp_message.json`:
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WABA_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {"display_phone_number": "15550001111", "phone_number_id": "PNID"},
            "contacts": [{"profile": {"name": "Ada"}, "wa_id": "15557654321"}],
            "messages": [
              {
                "from": "15557654321",
                "id": "wamid.HBgABC",
                "timestamp": "1717000000",
                "type": "text",
                "text": {"body": "Hello bot"}
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

`tests/fixtures/whatsapp_status.json`:
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WABA_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {"display_phone_number": "15550001111", "phone_number_id": "PNID"},
            "statuses": [
              {"id": "wamid.HBgABC", "status": "delivered", "timestamp": "1717000001"}
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_channel.py`:
```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -k parse -v`
Expected: FAIL with `AttributeError: 'WhatsAppChannel' object has no attribute 'parse'`

- [ ] **Step 4: Write minimal implementation**

Add this method to `WhatsAppChannel` in `app/channel.py`:
```python
    def parse(self, raw_body: bytes) -> InboundMessage | None:
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            return None
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                messages = change.get("value", {}).get("messages", [])
                for message in messages:
                    if message.get("type") == "text":
                        return InboundMessage(
                            conversation_id=message["from"],
                            text=message["text"]["body"],
                        )
        return None
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -v`
Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/channel.py plugins/chatbot-toolkit/reference-app/tests/test_channel.py plugins/chatbot-toolkit/reference-app/tests/fixtures
git commit -m "feat(chatbot): parse inbound WhatsApp text messages"
```

---

## Task 8: WhatsAppChannel — send via Graph API

**Files:**
- Modify: `plugins/chatbot-toolkit/reference-app/app/channel.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_channel.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_channel.py`:
```python
import asyncio

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -k send -v`
Expected: FAIL with `AttributeError: 'WhatsAppChannel' object has no attribute 'send'` (or a coroutine/await error)

- [ ] **Step 3: Write minimal implementation**

Add this method to `WhatsAppChannel` in `app/channel.py`:
```python
    async def send(self, message: OutboundMessage) -> None:
        client = self._client or httpx.AsyncClient()
        try:
            response = await client.post(
                f"{self._graph_url}/{self._phone_number_id}/messages",
                headers={"Authorization": f"Bearer {self._access_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": message.conversation_id,
                    "type": "text",
                    "text": {"body": message.text},
                },
            )
            response.raise_for_status()
        finally:
            if self._client is None:
                await client.aclose()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_channel.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/channel.py plugins/chatbot-toolkit/reference-app/tests/test_channel.py
git commit -m "feat(chatbot): send WhatsApp replies via Graph API"
```

---

## Task 9: Brain (Claude reply)

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/brain.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_brain.py`

- [ ] **Step 1: Write the failing test**

`tests/test_brain.py`:
```python
import asyncio
from types import SimpleNamespace

from app.brain import ClaudeBrain
from app.models import Message


class FakeMessages:
    def __init__(self, reply_text: str) -> None:
        self._reply_text = reply_text
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self._reply_text)])


class FakeAnthropic:
    def __init__(self, reply_text: str) -> None:
        self.messages = FakeMessages(reply_text)


def test_respond_returns_model_text_and_includes_history():
    fake = FakeAnthropic("Hi Ada!")
    brain = ClaudeBrain(model="claude-sonnet-4-6", client=fake)
    history = [Message(role="user", text="hello"), Message(role="assistant", text="hey")]

    reply = asyncio.run(brain.respond(history, "what's up?"))

    assert reply == "Hi Ada!"
    sent = fake.messages.calls[0]["messages"]
    assert sent == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hey"},
        {"role": "user", "content": "what's up?"},
    ]
    assert fake.messages.calls[0]["model"] == "claude-sonnet-4-6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_brain.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.brain'`

- [ ] **Step 3: Write minimal implementation**

`app/brain.py`:
```python
from typing import Protocol

from anthropic import AsyncAnthropic

from app.models import Message

SYSTEM_PROMPT = (
    "You are a helpful assistant replying to users on a messaging app. "
    "Keep replies concise and friendly."
)


class Brain(Protocol):
    async def respond(self, history: list[Message], incoming: str) -> str: ...


class ClaudeBrain:
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        client: AsyncAnthropic | None = None,
        max_tokens: int = 1024,
    ) -> None:
        self._client = client or AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def respond(self, history: list[Message], incoming: str) -> str:
        messages = [{"role": m.role, "content": m.text} for m in history]
        messages.append({"role": "user", "content": incoming})
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_brain.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/brain.py plugins/chatbot-toolkit/reference-app/tests/test_brain.py
git commit -m "feat(chatbot): add ClaudeBrain reply module"
```

---

## Task 10: Webhook factory + GET verify endpoint

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/webhook.py`
- Test: `plugins/chatbot-toolkit/reference-app/tests/test_webhook_integration.py`

- [ ] **Step 1: Write the failing test**

`tests/test_webhook_integration.py`:
```python
from fastapi.testclient import TestClient

from app.channel import WhatsAppChannel
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_webhook_integration.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.webhook'`

- [ ] **Step 3: Write minimal implementation**

`app/webhook.py`:
```python
from fastapi import FastAPI, Request, Response

from app.brain import Brain
from app.channel import Channel
from app.guardrails import Guardrails
from app.models import Message, OutboundMessage
from app.session import SessionStore


def create_app(
    channel: Channel,
    brain: Brain,
    store: SessionStore,
    guardrails: Guardrails,
) -> FastAPI:
    app = FastAPI()

    @app.get("/webhook")
    async def verify(request: Request) -> Response:
        challenge = channel.verify(dict(request.query_params))
        if challenge is None:
            return Response(status_code=403)
        return Response(content=challenge, media_type="text/plain")

    @app.post("/webhook")
    async def receive(request: Request) -> Response:
        raw = await request.body()
        if not channel.verify_signature(raw, request.headers):
            return Response(status_code=403)
        inbound = channel.parse(raw)
        if inbound is None:
            return Response(status_code=200)

        guard_in = guardrails.screen_input(inbound.text)
        if not guard_in.allowed:
            await channel.send(
                OutboundMessage(conversation_id=inbound.conversation_id, text=guard_in.text)
            )
            return Response(status_code=200)

        history = await store.get_history(inbound.conversation_id)
        reply = await brain.respond(history, guard_in.text)
        guard_out = guardrails.screen_output(reply)

        await store.append(inbound.conversation_id, Message(role="user", text=inbound.text))
        await store.append(
            inbound.conversation_id, Message(role="assistant", text=guard_out.text)
        )
        await channel.send(
            OutboundMessage(conversation_id=inbound.conversation_id, text=guard_out.text)
        )
        return Response(status_code=200)

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_webhook_integration.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/webhook.py plugins/chatbot-toolkit/reference-app/tests/test_webhook_integration.py
git commit -m "feat(chatbot): add webhook app factory + verify endpoint"
```

---

## Task 11: Webhook POST — full tracer-bullet round-trip

**Files:**
- Modify: `plugins/chatbot-toolkit/reference-app/tests/test_webhook_integration.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_webhook_integration.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest tests/test_webhook_integration.py -k post -v`
Expected: Both `post` tests run; they may already pass given Task 10's implementation. If `test_post_webhook_replies_via_graph` fails, read the assertion error and fix the flow in `app/webhook.py` (do NOT weaken the test). The signature-reject test must pass.

- [ ] **Step 3: Verify the full suite passes**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest -v`
Expected: all tests pass (session 2, channel 9, brain 1, webhook 4 = 16 passed)

- [ ] **Step 4: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/tests/test_webhook_integration.py
git commit -m "test(chatbot): end-to-end webhook round-trip with mocked Graph"
```

---

## Task 12: Default app factory + run docs

**Files:**
- Create: `plugins/chatbot-toolkit/reference-app/app/config.py`
- Create: `plugins/chatbot-toolkit/reference-app/app/main.py`
- Create: `plugins/chatbot-toolkit/reference-app/README.md`

- [ ] **Step 1: Write the config loader**

`app/config.py`:
```python
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    anthropic_model: str
    meta_app_secret: str
    meta_verify_token: str
    whatsapp_access_token: str
    whatsapp_phone_number_id: str


def load_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        meta_app_secret=os.environ["META_APP_SECRET"],
        meta_verify_token=os.environ["META_VERIFY_TOKEN"],
        whatsapp_access_token=os.environ["WHATSAPP_ACCESS_TOKEN"],
        whatsapp_phone_number_id=os.environ["WHATSAPP_PHONE_NUMBER_ID"],
    )
```

- [ ] **Step 2: Write the default factory**

`app/main.py`:
```python
from fastapi import FastAPI

from app.brain import ClaudeBrain
from app.channel import WhatsAppChannel
from app.config import load_settings
from app.guardrails import NoOpGuardrails
from app.session import InMemorySessionStore
from app.webhook import create_app


def create_default_app() -> FastAPI:
    settings = load_settings()
    channel = WhatsAppChannel(
        app_secret=settings.meta_app_secret,
        verify_token=settings.meta_verify_token,
        access_token=settings.whatsapp_access_token,
        phone_number_id=settings.whatsapp_phone_number_id,
    )
    brain = ClaudeBrain(
        model=settings.anthropic_model, api_key=settings.anthropic_api_key
    )
    return create_app(
        channel=channel,
        brain=brain,
        store=InMemorySessionStore(),
        guardrails=NoOpGuardrails(),
    )
```

- [ ] **Step 3: Write the reference-app README**

`plugins/chatbot-toolkit/reference-app/README.md`:
```markdown
# Reference App — Claude WhatsApp bot

A runnable, full-stack Claude-powered WhatsApp bot. Four deep modules behind
simple interfaces, wired by a thin FastAPI webhook:

- `Channel` — Meta webhook verify, signature check, parse, Graph API send.
- `Brain` — Claude reply (Anthropic Messages API; Agent SDK layered later).
- `SessionStore` — conversation history (in-memory here; Postgres later).
- `Guardrails` — input/output screening (no-op here; real screening later).

## Run

    cp .env.example .env   # fill in your values
    uv sync
    uv run uvicorn app.main:create_default_app --factory --host 0.0.0.0 --port 8000

Expose it publicly for Meta (dev):

    npx cloudflared tunnel --url http://localhost:8000
    # or: ngrok http 8000

Set the tunnel URL + `META_VERIFY_TOKEN` as the webhook callback in your Meta App.

## Test

    uv run pytest
```

- [ ] **Step 4: Verify config import and factory wiring (without real secrets)**

Run:
```bash
cd plugins/chatbot-toolkit/reference-app && uv run python -c "import app.main, app.config; print('imports ok')" && cd -
```
Expected: `imports ok` (no env access happens at import time)

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/reference-app/app/config.py plugins/chatbot-toolkit/reference-app/app/main.py plugins/chatbot-toolkit/reference-app/README.md
git commit -m "feat(chatbot): add config loader, default app factory, run docs"
```

---

## Task 13: scaffold-bot skill + taxonomy + catalog

**Files:**
- Create: `plugins/chatbot-toolkit/skills/scaffold-bot/SKILL.md`
- Modify: `plugins/hq-core/taxonomy.yml`
- Modify: `plugins/hq-core/catalog.json` (regenerated, do not hand-edit)

- [ ] **Step 1: Write the skill**

`plugins/chatbot-toolkit/skills/scaffold-bot/SKILL.md`:
```markdown
---
name: scaffold-bot
description: Stand up a full-stack Claude-powered WhatsApp bot from the chatbot-toolkit reference app — FastAPI webhook, Channel/Brain/SessionStore/Guardrails modules, end to end. Use when starting a new chatbot, scaffolding a messaging bot, or wiring Claude to WhatsApp/Instagram.
---

# Scaffold a Bot

Start from the bundled reference app — one runnable WhatsApp bot you copy and adapt.

## Quick start

    cp .env.example .env        # ANTHROPIC_API_KEY, META_* , WHATSAPP_*
    uv sync
    uv run uvicorn app.main:create_default_app --factory --port 8000
    npx cloudflared tunnel --url http://localhost:8000   # public HTTPS for Meta

The reference app lives at `reference-app/` in this plugin. Copy it into your repo
and adapt.

## Architecture

Four deep modules behind simple interfaces, wired by a thin webhook:

| Module | Interface | Swap for tests |
|--------|-----------|----------------|
| `Channel` | `verify` / `verify_signature` / `parse` / `send` | mock httpx transport |
| `Brain` | `respond(history, incoming) -> str` | stub brain |
| `SessionStore` | `get_history` / `append` | in-memory impl |
| `Guardrails` | `screen_input` / `screen_output` | no-op impl |

Flow: `parse → guard → load → brain → append → send`. The FastAPI layer is thin
glue; logic lives in the modules. Build the app via `create_app(channel, brain,
store, guardrails)` so you can inject fakes.

## Next steps

- Persist sessions in Postgres → `bot-session-state`
- Real safety screening → `bot-safety`
- Add Instagram → `meta-messaging`
- Deploy → `deploy-bot`
```

- [ ] **Step 2: Register the skill in the taxonomy**

In `plugins/hq-core/taxonomy.yml`, add this line to the `skills:` map (after `caveman: [meta]`):
```yaml
  scaffold-bot: [feature-dev]
```

- [ ] **Step 3: Regenerate the catalog**

Run:
```bash
cd /Users/pedrosasso/repos/pedrosasso2/hq && python3 scripts/build-catalog.py
```
Expected: `wrote plugins/hq-core/catalog.json (N entries)` with no errors (N is the previous count + 1).

- [ ] **Step 4: Verify CI checks pass locally**

Run:
```bash
cd /Users/pedrosasso/repos/pedrosasso2/hq
head -n1 plugins/chatbot-toolkit/skills/scaffold-bot/SKILL.md | grep -qx -- '---' && echo "frontmatter ok"
python3 scripts/build-catalog.py && git diff --exit-code plugins/hq-core/catalog.json && echo "catalog fresh"
```
Expected: `frontmatter ok`, then `catalog fresh` (no diff after regeneration → it was committed in the right state). If `git diff` shows changes, they are the new catalog entry — stage them in the commit below.

- [ ] **Step 5: Commit**

```bash
git add plugins/chatbot-toolkit/skills/scaffold-bot/SKILL.md plugins/hq-core/taxonomy.yml plugins/hq-core/catalog.json
git commit -m "feat(chatbot): add scaffold-bot skill + register in taxonomy/catalog"
```

---

## Task 14: CHANGELOG + full verification

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update the changelog**

In `CHANGELOG.md`, under `## [Unreleased]`, add a new section at the top:
```markdown
### Added — chatbot-toolkit (tracer bullet, issue #2)
- New optional plugin `chatbot-toolkit` with a runnable `reference-app/`: a
  full-stack Claude-powered WhatsApp bot (FastAPI webhook → `Channel` /
  `Brain` / `SessionStore` / `Guardrails` deep modules). WhatsApp inbound
  parse + `X-Hub-Signature-256` validation + Graph API send; Claude reply via
  the Anthropic Messages API; in-memory sessions + no-op guardrails as seams.
- `scaffold-bot` skill documenting the reference app; registered in
  `taxonomy.yml` (`[feature-dev]`) and `catalog.json`.
- Marketplace lists `chatbot-toolkit`.
```

- [ ] **Step 2: Run the whole reference-app suite**

Run: `cd plugins/chatbot-toolkit/reference-app && uv run pytest -v && cd -`
Expected: 16 passed.

- [ ] **Step 3: Run the repo CI checks locally**

Run:
```bash
cd /Users/pedrosasso/repos/pedrosasso2/hq
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); [json.load(open(f)) for f in __import__('glob').glob('plugins/*/.claude-plugin/plugin.json')]; print('json ok')"
python3 scripts/build-catalog.py && git diff --exit-code plugins/hq-core/catalog.json && echo "catalog fresh"
python3 scripts/check-workflows.py && echo "workflows ok"
```
Expected: `json ok`, `catalog fresh`, `workflows ok`.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(chatbot): changelog for chatbot-toolkit tracer bullet"
```

---

## Self-Review

**Spec coverage (issue #2 acceptance criteria):**
- chatbot-toolkit in marketplace + valid plugin.json (no version) → Task 1 ✅
- reference-app boots, uv-managed → Tasks 1, 12 ✅
- GET /webhook returns hub.challenge on valid token → Tasks 5, 10 ✅
- POST /webhook valid signature → parse → Brain → Graph send → Tasks 6–11 ✅
- POST /webhook rejects invalid signature → Tasks 6, 11 ✅
- SessionStore + Channel protocols defined; in-memory + WhatsApp impls; Guardrails no-op seam → Tasks 3, 4, 5–8 ✅
- Brain wraps Claude; model default latest Sonnet, env-configurable → Tasks 9, 12 ✅
- Webhook integration test, mocked Graph + Anthropic → Task 11 ✅
- scaffold-bot skill + taxonomy [feature-dev] + catalog regen + CI green → Tasks 13, 14 ✅
- CHANGELOG updated → Task 14 ✅

**Placeholder scan:** No TBD/TODO/"handle edge cases"; every code step shows complete code. ✅

**Type consistency:** `InboundMessage(conversation_id, text)`, `OutboundMessage(conversation_id, text)`, `Message(role, text)` used identically across session/channel/brain/webhook. `Channel` methods `verify`/`verify_signature`/`parse`/`send` consistent between protocol, impl, and tests. `Brain.respond(history, incoming)` consistent across brain, stub, and webhook. Signature header `x-hub-signature-256` lowercased consistently. ✅

**Known risk flagged:** Brain uses Anthropic Messages API, not Agent SDK (intentional tracer-bullet simplification; slice #6 deepens behind the stable `respond()` interface). `anthropic>=0.40` and `graph.facebook.com/v21.0` should be confirmed current at execution time via Context7.
