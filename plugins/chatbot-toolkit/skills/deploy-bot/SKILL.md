---
name: deploy-bot
description: Get the chatbot-toolkit reference app onto a public HTTPS endpoint Meta will accept — build the bundled Dockerfile and deploy to a container PaaS (Fly / Railway / Render) with env/secret config, or tunnel to your laptop for dev. Use when deploying a bot, Dockerizing the reference app, setting up a webhook URL Meta accepts, configuring deploy secrets, or exposing a local bot for webhook testing.
---

# Deploy a Bot

Meta only delivers webhooks to a **public HTTPS** URL. Two paths: tunnel to your
laptop for development, or deploy the container to a PaaS for anything real. Both
end at the same callback URL — `https://<host>/webhook` — that you register in
the Meta App (see `meta-messaging`).

## Dev: tunnel to your laptop

Run the app locally and expose it over HTTPS:

    uv run uvicorn app.main:create_default_app --factory --host 0.0.0.0 --port 8000
    npx cloudflared tunnel --url http://localhost:8000   # or: ngrok http 8000

Use the printed `https://…` URL + your `META_VERIFY_TOKEN` as the webhook
callback. The tunnel URL changes on each restart (free tier), so re-paste it in
the Meta App when it rotates. Tunnels are for development only — they die with
your laptop.

## Prod: container PaaS

### Build

The reference app ships a multi-stage `Dockerfile` (`reference-app/Dockerfile`).
It installs dependencies with `uv sync --locked --no-dev`, ships only the venv
(non-editable install), runs as a non-root user, and starts uvicorn bound to
`$PORT` (falling back to 8000):

    docker build -t my-bot reference-app/
    docker run -p 8000:8000 --env-file reference-app/.env my-bot

A PaaS injects `$PORT` and terminates HTTPS for you, so the same image runs
unchanged.

### Deploy

Pick any container PaaS — they all build the `Dockerfile`, give you a public
HTTPS hostname, and inject secrets as env vars:

| Platform | Deploy | Set secrets |
|----------|--------|-------------|
| **Fly.io** | `fly launch` (detects the Dockerfile) → `fly deploy` | `fly secrets set ANTHROPIC_API_KEY=… META_APP_SECRET=…` |
| **Railway** | new project → deploy from repo (root = `reference-app/`) | Variables tab |
| **Render** | new Web Service, Docker runtime, root = `reference-app/` | Environment tab |

All three give you `https://<app>.<platform>.app` with managed TLS — register
`https://<host>/webhook` as the Meta callback.

### Secrets

Every value in `.env.example` must be set as a **platform secret**, never baked
into the image or committed:

    ANTHROPIC_API_KEY  META_APP_SECRET  META_VERIFY_TOKEN
    WHATSAPP_ACCESS_TOKEN  WHATSAPP_PHONE_NUMBER_ID  DATABASE_URL

`META_APP_SECRET` signs every inbound webhook (`X-Hub-Signature-256`) and
`ANTHROPIC_API_KEY` bills your account — leaking either is a real incident.
`.dockerignore` already excludes `.env` from the build context so local secrets
never land in an image layer.

`DATABASE_URL` points at managed Postgres (Fly Postgres, Railway/Render
Postgres add-on) for durable sessions — see `bot-session-state`.

## Verify the deploy

After the first deploy, confirm the verify handshake before pointing Meta at it:

    curl "https://<host>/webhook?hub.mode=subscribe&hub.verify_token=<your-token>&hub.challenge=ok"
    # → ok

A `403` means `META_VERIFY_TOKEN` doesn't match what you sent. Then register the
callback in the Meta App and send a test message.
