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
