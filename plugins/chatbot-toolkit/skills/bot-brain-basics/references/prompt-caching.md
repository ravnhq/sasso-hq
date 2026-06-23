# Prompt caching for a bot Brain

A bot resends a large stable prefix every turn — system prompt, tool definitions,
and the growing conversation history. Caching that prefix is the single biggest
cost lever a Brain has.

## The one invariant

**Caching is a prefix match. Any byte change anywhere in the prefix invalidates
everything after it.** Render order is `tools` → `system` → `messages`. A
breakpoint on the last system block caches tools + system together.

## Cache the frozen prefix

```python
response = await client.messages.create(
    model=self._model,
    max_tokens=self._max_tokens,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},   # 5-min TTL; "ttl": "1h" for longer
    }],
    messages=messages,
)
```

Top-level `cache_control={"type": "ephemeral"}` on `messages.create` is the
simplest option when you don't need fine-grained placement — it auto-marks the last
cacheable block.

## Multi-turn history

Put a breakpoint on the last content block of the most recently appended turn. Each
turn then reuses the entire prior conversation prefix, and hits accrue as the chat
grows. Max 4 breakpoints per request.

## Verify hits

```python
print(response.usage.cache_creation_input_tokens)  # written this turn (~1.25x)
print(response.usage.cache_read_input_tokens)       # served from cache (~0.1x)
print(response.usage.input_tokens)                  # uncached remainder
```

If `cache_read_input_tokens` is 0 across turns with the same prefix, a silent
invalidator is at work.

## Silent invalidators — audit the prefix for these

| Pattern | Why it breaks caching |
|---|---|
| `datetime.now()` / a timestamp in the system prompt | prefix changes every request |
| a UUID, request id, or session id early in the prefix | every request is unique |
| `json.dumps(d)` without `sort_keys=True` for tool defs | non-deterministic byte order |
| conditional system sections (`if flag: system += ...`) | each combo is a distinct prefix |
| changing the tool set or model mid-conversation | tools render first; full rebuild |

Fix by keeping the system prompt frozen and injecting any per-turn context as
message content after the breakpoint, not in the system prompt.

## Minimum cacheable prefix

Caching silently no-ops below a model-dependent minimum (e.g. ~4096 tokens on
Opus/Haiku 4.5, ~2048 on Sonnet 4.6) — you'll see `cache_creation_input_tokens: 0`
with no error. A short bot prompt may not be worth caching until tool defs and
history grow it past the floor.
