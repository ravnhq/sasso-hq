from typing import Protocol

import asyncpg

from app.models import Message

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    seq             BIGSERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role            TEXT NOT NULL,
    text            TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS messages_conversation_seq
    ON messages (conversation_id, seq);
"""


class SessionStore(Protocol):
    async def get_history(self, conversation_id: str) -> list[Message]: ...
    async def append(self, conversation_id: str, message: Message) -> None: ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._data: dict[str, list[Message]] = {}

    async def get_history(self, conversation_id: str) -> list[Message]:
        return list(self._data.get(conversation_id, []))

    async def append(self, conversation_id: str, message: Message) -> None:
        self._data.setdefault(conversation_id, []).append(message)


class PostgresSessionStore:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._dsn)
            async with self._pool.acquire() as conn:
                await conn.execute(_SCHEMA)
        return self._pool

    async def get_history(self, conversation_id: str) -> list[Message]:
        pool = await self._get_pool()
        rows = await pool.fetch(
            "SELECT role, text FROM messages "
            "WHERE conversation_id = $1 ORDER BY seq",
            conversation_id,
        )
        return [Message(role=row["role"], text=row["text"]) for row in rows]

    async def append(self, conversation_id: str, message: Message) -> None:
        pool = await self._get_pool()
        await pool.execute(
            "INSERT INTO messages (conversation_id, role, text) "
            "VALUES ($1, $2, $3)",
            conversation_id,
            message.role,
            message.text,
        )
