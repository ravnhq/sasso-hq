import hashlib
import hmac
import json
from typing import Any, Mapping, Protocol

import httpx

from app.models import InboundMessage, OutboundMessage


class Channel(Protocol):
    def verify(self, params: Mapping[str, str]) -> str | None: ...
    def verify_signature(self, raw_body: bytes, headers: Mapping[str, str]) -> bool: ...
    def parse(self, raw_body: bytes) -> InboundMessage | None: ...
    async def send(self, message: OutboundMessage) -> None: ...


class MetaChannel:
    """Shared Meta plumbing: the webhook handshake, X-Hub-Signature-256
    validation, and the authenticated Graph POST. Channels differ only in how
    they parse inbound payloads and shape outbound sends."""

    def __init__(
        self,
        app_secret: str,
        verify_token: str,
        access_token: str,
        graph_url: str = "https://graph.facebook.com/v21.0",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._app_secret = app_secret
        self._verify_token = verify_token
        self._access_token = access_token
        self._graph_url = graph_url
        self._client = client

    def verify(self, params: Mapping[str, str]) -> str | None:
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == self._verify_token
        ):
            return params.get("hub.challenge")
        return None

    def verify_signature(self, raw_body: bytes, headers: Mapping[str, str]) -> bool:
        provided = headers.get("x-hub-signature-256")
        if not provided:
            return False
        expected = (
            "sha256="
            + hmac.new(self._app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
        )
        return hmac.compare_digest(provided, expected)

    async def _post(self, path: str, body: dict[str, Any]) -> None:
        client = self._client or httpx.AsyncClient()
        try:
            response = await client.post(
                f"{self._graph_url}/{path}",
                headers={"Authorization": f"Bearer {self._access_token}"},
                json=body,
            )
            response.raise_for_status()
        finally:
            if self._client is None:
                await client.aclose()


class WhatsAppChannel(MetaChannel):
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
        super().__init__(app_secret, verify_token, access_token, graph_url, client)
        self._phone_number_id = phone_number_id

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

    async def send(self, message: OutboundMessage) -> None:
        await self._post(
            f"{self._phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "to": message.conversation_id,
                "type": "text",
                "text": {"body": message.text},
            },
        )


class InstagramChannel(MetaChannel):
    name = "instagram"

    def __init__(
        self,
        app_secret: str,
        verify_token: str,
        access_token: str,
        ig_id: str,
        graph_url: str = "https://graph.facebook.com/v21.0",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(app_secret, verify_token, access_token, graph_url, client)
        self._ig_id = ig_id

    def parse(self, raw_body: bytes) -> InboundMessage | None:
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            return None
        for entry in payload.get("entry", []):
            for event in entry.get("messaging", []):
                message = event.get("message", {})
                if message.get("is_echo"):
                    continue
                if "text" in message:
                    return InboundMessage(
                        conversation_id=event["sender"]["id"],
                        text=message["text"],
                    )
        return None

    async def send(self, message: OutboundMessage) -> None:
        await self._post(
            f"{self._ig_id}/messages",
            {
                "recipient": {"id": message.conversation_id},
                "message": {"text": message.text},
            },
        )
