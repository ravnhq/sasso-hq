# The 24-hour window and message templates

WhatsApp gates what a business may send on a **24-hour customer service
window**. Meta also uses this window as the unit for conversation-based
pricing.

## When the window is open

The window opens (or refreshes) for 24 hours each time you reply to a message
the user sent you. While it is open you can send **free-form, non-template**
messages — plain text, media, interactive messages. The reference app's
`WhatsAppChannel.send` sends free-form text, which is all you need to answer a
user who just messaged you.

## When the window is closed

To **initiate** a conversation, or to message a user more than 24 hours after
their last message, free-form sends are rejected. You must send a
**pre-approved message template**. The Graph API call is the same
`/{phone_number_id}/messages` endpoint, with `"type": "template"`:

    {
      "messaging_product": "whatsapp",
      "to": "<wa_id>",
      "type": "template",
      "template": {
        "name": "<approved_template_name>",
        "language": {"code": "en_US"},
        "components": [ ... ]   // fill body/header variables if the template has them
      }
    }

`components` is only needed when the template has variables (body parameters,
header media, button payloads). A template with no variables sends with just
`name` and `language`.

## Template categories

Every template is submitted for approval under a category, which governs
allowed content and pricing:

| Category | Use for |
|----------|---------|
| `MARKETING` | promotions, offers, announcements |
| `UTILITY` | transactional updates tied to an action (order, appointment, account) |
| `AUTHENTICATION` | one-time passcodes / login verification |

Create and submit templates in WhatsApp Manager (or the Message Templates API)
and wait for approval before sending them.

## Sources

- WhatsApp Business Platform — Get Started (24-hour window, template
  fundamentals, message categories):
  <https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started>
- Pricing (conversation = 24-hour window):
  <https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started>

Verified against Meta docs (May 2026). The 24-hour rule, the
template-required-outside-window rule, and the marketing/utility/authentication
categories are confirmed. Exact template payload fields can change between Graph
versions — check the current Message API reference when you build templates.
