# Sending media

WhatsApp media messages (image, audio, video, document, sticker) reference the
file one of two ways. Both go to the same `/{phone_number_id}/messages`
endpoint as text, just with a different `type` and object.

## By uploaded media ID

Upload the file once to Meta, get back an `id`, then reference it. Best for
files you reuse, or that aren't publicly hosted.

1. Upload to `POST /{phone_number_id}/media` (multipart: the file +
   `messaging_product=whatsapp`). The response returns a media `id`.
2. Send referencing that id:

       {
         "messaging_product": "whatsapp",
         "to": "<wa_id>",
         "type": "image",
         "image": {"id": "<media_id>", "caption": "optional"}
       }

## By link URL

Skip the upload and point at a public HTTPS URL. Meta fetches it and **caches
it for ~10 minutes**, reusing the cached asset for later sends with the same
link. To force a re-fetch within that window, append a random query string so
Meta treats it as a new asset.

    {
      "messaging_product": "whatsapp",
      "to": "<wa_id>",
      "type": "document",
      "document": {"link": "https://example.com/file.pdf", "filename": "file.pdf"}
    }

## Per-type notes

- **image** — single image, optional `caption`.
- **audio** — shows a play control; no caption.
- **document** — set `filename` so the recipient sees a sensible name.
- **video** — optional `caption`.
- **sticker** — WebP; no caption.

Swap the `type` value and the matching object key (`image` / `audio` /
`video` / `document` / `sticker`); each takes either `id` or `link`.

## Sources

- Media API reference (media ID, 10-minute link cache, append query string to
  bust it):
  <https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media/>
- Media Upload API:
  <https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/media-upload-api>
- Image / audio / document message guides:
  <https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages/>

Verified against Meta docs (May 2026): the upload-for-media-id vs link-URL
distinction and the ~10-minute link cache (with the random-query-string
cache-bust) are confirmed. Per-type object shapes can vary slightly by Graph
version — check the current Messages reference.
