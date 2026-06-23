---
name: bot-session-state
description: Persist bot conversation history in Postgres using the chatbot-toolkit reference app's PostgresSessionStore — asyncpg, a lazy pool, and a temp-Postgres test. Use when sessions must survive restarts, moving a bot off in-memory storage, or adding a durable SessionStore.
---

# Bot Session State (Postgres)

The reference app ships two `SessionStore` implementations behind one Protocol
(`get_history` / `append`). `InMemorySessionStore` is the test seam;
`PostgresSessionStore` is what you run in production so history survives
restarts. Both live in `reference-app/app/session.py`.

## Schema

One row per message, ordered by a monotonic key per conversation:

    CREATE TABLE IF NOT EXISTS messages (
        seq             BIGSERIAL PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role            TEXT NOT NULL,
        text            TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS messages_conversation_seq
        ON messages (conversation_id, seq);

`get_history` reads `WHERE conversation_id = $1 ORDER BY seq`, so append order is
preserved and conversations are isolated by the keyed lookup.

## Lazy pool

`create_default_app()` is synchronous, so the store can't open a connection in
`__init__`. Instead `PostgresSessionStore(dsn)` just stashes the DSN; the
asyncpg pool is created once on first use and the `CREATE TABLE IF NOT EXISTS`
runs on that first connect:

    async def _get_pool(self):
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._dsn)
            async with self._pool.acquire() as conn:
                await conn.execute(_SCHEMA)
        return self._pool

`get_history` / `append` call `_get_pool()` then run one query each.

## Wiring

`app/main.py` builds the store from `settings.database_url` (env `DATABASE_URL`,
see `.env.example`) and injects it into `create_app(...)`. The webhook flow
(`parse → guard → load → brain → append → send`) is unchanged — it already calls
`store.get_history` before the Brain and `store.append` for both the inbound and
outbound message after. Swapping in-memory for Postgres is a one-line change at
the composition root.

## Testing with a temp Postgres

Tests use `pytest-postgresql`, which boots a throwaway real Postgres from the
locally-installed binaries (it finds them via `pg_config` on PATH — Postgres.app
works, no Docker). The `postgresql` client fixture yields a connection; build the
asyncpg DSN from its params and drive the async store with `asyncio.run`:

    def _dsn(postgresql):
        i = postgresql.info
        return f"postgresql://{i.user}@{i.host}:{i.port}/{i.dbname}"

The temp DB uses trust auth (no password), so the DSN omits one. Tests assert
append-then-get preserves order and that a second conversation_id stays empty.

## Next steps

- Real safety screening → `bot-safety`
- Deploy with a managed Postgres → `deploy-bot`
