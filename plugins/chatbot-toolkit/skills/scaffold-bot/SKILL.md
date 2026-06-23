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
