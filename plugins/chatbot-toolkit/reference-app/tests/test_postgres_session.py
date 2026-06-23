import asyncio

from app.models import Message
from app.session import PostgresSessionStore


def _dsn(postgresql) -> str:
    info = postgresql.info
    return f"postgresql://{info.user}@{info.host}:{info.port}/{info.dbname}"


def test_append_then_get_preserves_order(postgresql):
    store = PostgresSessionStore(_dsn(postgresql))

    async def scenario() -> list[Message]:
        await store.append("c1", Message(role="user", text="hi"))
        await store.append("c1", Message(role="assistant", text="hello"))
        return await store.get_history("c1")

    assert asyncio.run(scenario()) == [
        Message(role="user", text="hi"),
        Message(role="assistant", text="hello"),
    ]


def test_conversations_are_isolated(postgresql):
    store = PostgresSessionStore(_dsn(postgresql))

    async def scenario() -> list[Message]:
        await store.append("c1", Message(role="user", text="a"))
        return await store.get_history("c2")

    assert asyncio.run(scenario()) == []
