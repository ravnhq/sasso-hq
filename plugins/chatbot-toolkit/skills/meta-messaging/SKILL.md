---
name: meta-messaging
description: Connect the chatbot-toolkit reference app to Meta — create a Meta App, pass the webhook verify handshake, validate X-Hub-Signature-256, and send via the Meta Graph API for WhatsApp and Instagram. Use when setting up a Meta App, wiring a WhatsApp or Instagram webhook, debugging webhook verification or signature failures, parsing inbound payloads, or sending WhatsApp templates/media or Instagram DMs.
---

# Meta Messaging

How the reference app talks to Meta: webhook in, Graph API out. All the code
referenced here lives in `reference-app/app/channel.py` and
`reference-app/app/webhook.py`. Env var names come from `app/config.py` and
`.env.example`.

Both channels — `WhatsAppChannel` and `InstagramChannel` — subclass
`MetaChannel`, which owns the parts Meta makes identical across products: the
verify handshake, the `X-Hub-Signature-256` check, and the authenticated Graph
POST. A channel only overrides `parse` (inbound payload shape) and `send`
(outbound body + endpoint). `webhook.py` never names a concrete channel, so the
same `parse → guard → load → brain → append → send` flow serves either; pick one
per instance with the `CHANNEL` env var (`whatsapp` default, or `instagram`).

## 1. Create a Meta App

1. At [developers.facebook.com](https://developers.facebook.com), create an app
   (Business type) and add the **WhatsApp** product.
2. The product gives you a test **phone number ID** and a temporary **access
   token**. Note both.
3. App Dashboard → Settings → Basic exposes the **App Secret** — this signs
   every webhook payload.
4. Pick your own **verify token** — any random string; you'll paste the same
   value into Meta and your env.

Map these onto the app's env (`.env.example`):

| Env var | Meta source |
|---------|-------------|
| `META_APP_SECRET` | App Settings → Basic → App Secret (signs both products' webhooks) |
| `META_VERIFY_TOKEN` | a random string you choose |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp product → API setup |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp product → API setup |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram product → API setup (page/IG access token) |
| `INSTAGRAM_ID` | the messaging Instagram account ID (the webhook's `entry[].id`) |

`META_APP_SECRET` and `META_VERIFY_TOKEN` are shared — one Meta App signs and
verifies both products. Only the per-product token/ID pair differs.

## 2. Subscribe the webhook + pass the handshake

Expose your local app over HTTPS (Meta requires it) and register the callback:

    npx cloudflared tunnel --url http://localhost:8000   # public HTTPS

In the WhatsApp product → Configuration, set:

- **Callback URL**: `https://<tunnel>/webhook`
- **Verify token**: the same string as `META_VERIFY_TOKEN`

Meta then sends a `GET /webhook` with `hub.mode=subscribe`, `hub.verify_token`,
and `hub.challenge`. `WhatsAppChannel.verify` checks the mode and token match,
then returns the challenge; the GET endpoint in `webhook.py` echoes it back as
plain text (403 otherwise). That single round-trip is the whole handshake.

After it succeeds, subscribe to the **messages** field so inbound messages
start arriving as `POST /webhook`.

## 3. Validate `X-Hub-Signature-256`

Every POST carries an `X-Hub-Signature-256` header. The webhook reads the
**raw body before parsing** and passes it to `WhatsAppChannel.verify_signature`,
which recomputes `sha256=` + HMAC-SHA256 of the raw bytes keyed by the app
secret and compares with `hmac.compare_digest` (constant-time). A mismatch or
missing header returns 403 before the brain ever runs.

Two things that quietly break this:

- **Re-serializing the body.** The HMAC is over the exact bytes Meta sent.
  Parse to JSON only *after* verifying — which is why `webhook.py` does
  `raw = await request.body()` first.
- **Header casing.** The lookup uses lowercase `x-hub-signature-256`; Starlette
  headers are case-insensitive, so this is fine in the app, but worth knowing
  if you reimplement the check elsewhere.

## 4. Send via the Graph API

`WhatsAppChannel.send` POSTs to
`{graph_url}/{phone_number_id}/messages` with a Bearer access token and a body
that always starts with `"messaging_product": "whatsapp"`. The reference app
pins the Graph version to **`v21.0`** (`graph_url` default in `channel.py`); Meta
ships a new version every few months, so bump it deliberately rather than by
accident. The text payload it sends:

    {
      "messaging_product": "whatsapp",
      "to": "<wa_id>",
      "type": "text",
      "text": {"body": "..."}
    }

`response.raise_for_status()` surfaces Graph errors (expired token, outside the
messaging window, unapproved template) instead of swallowing them.

## WhatsApp: the 24-hour window, templates, and media

WhatsApp is not free-form like a generic chat channel. What you may send
depends on whether a **24-hour customer service window** is open.

- Replying to a user's inbound message opens (or refreshes) a 24-hour window.
  Inside it you may send **free-form / non-template** messages — exactly the
  text the reference app's `send` produces.
- Outside the window — or to start a conversation the user didn't — you must
  send a **pre-approved message template**. Templates are categorized as
  **marketing**, **utility**, or **authentication**, and the category affects
  approval and pricing.
- **Media** (image, audio, document, video, sticker) is sent either by an
  uploaded **media ID** (upload once to Meta, reuse the ID) or by a public
  **link** URL (Meta fetches and caches it ~10 minutes).

The reference app only sends text, which is enough while a window is open. For
the exact template and media request payloads, see:

- [references/whatsapp-window.md](references/whatsapp-window.md) — window rules + template categories
- [references/whatsapp-media.md](references/whatsapp-media.md) — media ID vs link, per-type payloads

## Instagram: the second channel

Add the **Instagram** product to the same Meta App, connect a professional
(business/creator) Instagram account, and subscribe the **messages** field.
Verify and signature validation are byte-identical to WhatsApp — that's why both
channels share `MetaChannel`. Two things genuinely differ: the inbound payload
shape and the send body.

**Inbound payload.** Instagram does *not* use WhatsApp's
`entry[].changes[].value.messages[]`. It uses the Messenger-style envelope
`object: "instagram"` → `entry[].messaging[]`, where each event carries
`sender.id` (the Instagram-scoped sender ID, your `conversation_id`),
`recipient.id`, and `message.{mid, text}`:

    {
      "object": "instagram",
      "entry": [{
        "id": "<IG account id>",
        "messaging": [{
          "sender": {"id": "<IGSID>"},
          "recipient": {"id": "<IG account id>"},
          "message": {"mid": "...", "text": "Hello bot"}
        }]
      }]
    }

`InstagramChannel.parse` walks `entry[].messaging[]`, **skips any event whose
`message.is_echo` is true** (those are your own sent messages echoed back — not
skipping them loops the bot against itself), and returns the first text message.

**Send.** `InstagramChannel.send` POSTs to `{graph_url}/{ig_id}/messages` with
the Messenger envelope — and crucially **no `messaging_product` field** (that is
WhatsApp-only):

    {
      "recipient": {"id": "<IGSID>"},
      "message": {"text": "..."}
    }

The reference app defaults `graph_url` to `https://graph.facebook.com/v21.0` —
the **Instagram API with Facebook Login** path, where the IG account is linked to
a Facebook Page and you send with a Page access token. If you instead use the
**Instagram API with Instagram Login** (standalone, no Page), point `graph_url`
at `https://graph.instagram.com/v21.0` and use an Instagram user access token;
the request body is the same.

For the DM 24-hour window, story replies/mentions, and reactions, see:

- [references/instagram-messaging.md](references/instagram-messaging.md) — DM window, story/reaction events, login variants

## Next steps

- Scaffold the app these modules live in → `scaffold-bot`
- Persist sessions across the window → `bot-session-state`
- Screen inbound/outbound content → `bot-safety`
- Deploy with a stable HTTPS URL → `deploy-bot`
