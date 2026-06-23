# Instagram DM rules: window, stories, reactions

What `InstagramChannel` must know beyond the plain text DM that the reference
app handles. Inbound shapes here all arrive in the same `entry[].messaging[]`
events that `parse` already walks; the app currently acts only on text, but
these are the variants you'll meet.

## The 24-hour messaging window

Instagram gates sends on a **24-hour window**, like WhatsApp. The window opens
or refreshes each time the user messages you; inside it you may send free-form
replies — exactly the text `send` produces. Outside it, a standard send is
rejected and you must attach a **message tag** (e.g. `HUMAN_AGENT`, which extends
the window to 7 days where approved) via `messaging_type` / `tag` params rather
than the plain `{recipient, message}` body. There is **no template system** like
WhatsApp's — tags, not templates, are how you reach a user outside the window.

Text is UTF-8 and capped at **1000 bytes** per message.

## Echoes

When your app sends a message, Meta echoes it back as a `messaging` event with
`message.is_echo: true` (via the `message_echoes` field if subscribed). On an
echo, `sender.id` and `recipient.id` are swapped versus an inbound message, so
`is_echo` — not the IDs — is the reliable discriminator. `InstagramChannel.parse`
skips these; without that guard the bot replies to its own replies.

## Story replies and mentions

A user replying to your story arrives as a normal `messages` text event with a
`reply_to.story` block naming the story:

    "message": {
      "mid": "...",
      "text": "Love this!",
      "reply_to": {"story": {"id": "<story id>", "url": "<cdn url>"}}
    }

A story *mention* (the user tags you in their story) arrives as an attachment of
type `story_mention` in `message.attachments[]`. The reference app's `parse`
returns text, so a plain story reply already flows through; mentions and other
attachments would need attachment handling to act on.

## Reactions

Reactions (❤️ etc.) arrive on the separate `message_reactions` field, not as a
message:

    "reaction": {"mid": "<message id>", "action": "react", "reaction": "love", "emoji": "❤️"}

## Login variants

| | Facebook Login | Instagram Login |
|---|---|---|
| Graph base | `https://graph.facebook.com` | `https://graph.instagram.com` |
| Account model | IG linked to a Facebook Page | standalone IG professional account |
| Token | Page access token | Instagram user access token |
| Send endpoint | `/<PAGE_ID>/messages` | `/<IG_ID>/messages` |

The send body (`{recipient: {id}, message: {text}}`, no `messaging_product`) is
identical for both — only `graph_url`, the ID, and the token differ. The
reference app defaults to the Facebook Login path; pass a different `graph_url`
to `InstagramChannel` for Instagram Login.

## Sources

- Instagram Platform — Webhooks (verify handshake, `X-Hub-Signature-256`, fields,
  payload examples):
  <https://developers.facebook.com/docs/instagram-platform/webhooks/>
- Instagram API with Instagram Login — Messaging (send API, window, tags):
  <https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api/>
- Send a message (Instagram via Messenger Platform / Facebook Login):
  <https://developers.facebook.com/docs/messenger-platform/instagram/features/send-message/>

Verified against Meta docs (June 2026): the `object: "instagram"` →
`entry[].messaging[]` shape, the `is_echo` echo marker, the
`{recipient, message}` send body with no `messaging_product`, and the two login
variants are confirmed. Pin the Graph version deliberately — Instagram messaging
is available on v21+ and Meta ships new versions every few months.
