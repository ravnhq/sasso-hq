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
