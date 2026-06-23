# Reference App — Claude Meta messaging bot

A runnable, full-stack Claude-powered Meta messaging bot (WhatsApp and
Instagram). Four deep modules behind simple interfaces, wired by a thin
FastAPI webhook:

- `Channel` — Meta webhook verify, signature check, parse, Graph API send.
  `WhatsAppChannel` and `InstagramChannel` share a `MetaChannel` base; pick one
  per instance with the `CHANNEL` env var (`whatsapp` default, or `instagram`).
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
