import asyncio

from app.models import Message
from app.session import InMemorySessionStore


def test_append_then_get_preserves_order():
    store = InMemorySessionStore()
    asyncio.run(store.append("c1", Message(role="user", text="hi")))
    asyncio.run(store.append("c1", Message(role="assistant", text="hello")))
    history = asyncio.run(store.get_history("c1"))
    assert history == [
        Message(role="user", text="hi"),
        Message(role="assistant", text="hello"),
    ]


def test_conversations_are_isolated():
    store = InMemorySessionStore()
    asyncio.run(store.append("c1", Message(role="user", text="a")))
    assert asyncio.run(store.get_history("c2")) == []
