---
name: bot-brain-basics
description: Teach the raw Anthropic Python SDK behind the reference app's Brain — messages.create, the tool-use loop, streaming, and prompt caching. Use when implementing or extending a bot Brain, calling Claude directly, adding tools/streaming/caching to messages.create, or asking how ClaudeBrain talks to the model.
---

# Bot Brain Basics — the raw Anthropic SDK

The reference app's `Brain` is deliberately thin: one call to the raw Anthropic
Messages API behind a one-method interface. Simplest thing that's correct, and
trivially mockable in tests. This skill teaches that raw SDK so you can extend it
with confidence.

The shipped code is the single source of truth:
`reference-app/app/brain.py` defines

    class Brain(Protocol):
        async def respond(self, history: list[Message], incoming: str) -> str: ...

and `ClaudeBrain` implements it with `AsyncAnthropic` + `await
self._client.messages.create(...)`, concatenating the text blocks of the reply.
`Message` (role + text) lives in `reference-app/app/models.py`. Everything below
layers onto that one `messages.create` call.

## The one call the app makes today

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY from the environment

response = await client.messages.create(
    model="claude-haiku-4-5",          # current model id; see notes below
    max_tokens=1024,
    system=SYSTEM_PROMPT,
    messages=[{"role": m.role, "content": m.text} for m in history]
             + [{"role": "user", "content": incoming}],
)
reply = "".join(b.text for b in response.content if b.type == "text")
```

`response.content` is a list of typed blocks — always check `.type` before
reading `.text`, because thinking and tool-use blocks can appear in the list too.
The API is stateless: you send the full `history` every turn. That's exactly what
`SessionStore` exists to hold.

## Adding tools — the tool-use loop

Give Claude tools, then loop: call the model, run any tools it asks for, feed the
results back, repeat until it stops asking. Keep the loop inside `respond()` so the
interface doesn't change.

```python
while True:
    response = await client.messages.create(
        model=self._model, max_tokens=self._max_tokens,
        system=SYSTEM_PROMPT, messages=messages, tools=tools,
    )
    if response.stop_reason == "end_turn":
        break
    messages.append({"role": "assistant", "content": response.content})
    results = [
        {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
        for b in response.content if b.type == "tool_use"
    ]
    messages.append({"role": "user", "content": results})
```

Three rules that bite if you skip them:

- Append the **whole** `response.content` back as the assistant turn before sending
  results — that preserves the `tool_use` blocks the API expects to see.
- Each `tool_result` must carry the matching `tool_use_id`. One result per tool call.
- Parse `tool.input` as the structured object it already is — never string-match the
  serialized JSON.

The SDK also ships a `@beta_tool` decorator + `client.beta.messages.tool_runner()`
that runs this loop for you. Use it when you don't need to gate or log each call;
hand-roll the loop (above) when you do. See `references/tool-use.md`.

## Streaming

For a chat-style bot, stream so you can forward tokens as they arrive instead of
blocking on the full reply:

```python
async with client.messages.stream(
    model=self._model, max_tokens=self._max_tokens,
    system=SYSTEM_PROMPT, messages=messages,
) as stream:
    async for text in stream.text_stream:
        ...                      # forward each chunk
    final = await stream.get_final_message()   # full Message, for usage/history
```

`get_final_message()` gives you the complete reply (and `usage`) after streaming —
so you keep timeout protection without hand-handling every event.

## Prompt caching — do this

A bot resends a large stable prefix (system prompt, tool defs, conversation
history) every turn. Cache it. Caching is a **prefix match**: mark the end of the
stable part with `cache_control` and reuse pays ~0.1x for the cached tokens.

```python
response = await client.messages.create(
    model=self._model, max_tokens=self._max_tokens,
    system=[{"type": "text", "text": SYSTEM_PROMPT,
             "cache_control": {"type": "ephemeral"}}],
    messages=messages,
)
print(response.usage.cache_read_input_tokens)   # > 0 means a hit
```

Keep the system prompt **frozen** — no `datetime.now()`, no per-request IDs ahead
of the breakpoint, or every request misses. Verify hits via
`usage.cache_read_input_tokens`. Full placement patterns and the silent-invalidator
checklist: `references/prompt-caching.md`.

## Model ids

Use current Claude 4.x ids — `claude-opus-4-8`, `claude-sonnet-4-6`,
`claude-haiku-4-5`. A chat bot defaults well to Haiku (fast, cheap) or Sonnet; the
reference app picks the model from config. On Opus 4.8/4.7 the thinking/sampling
surface differs — see `references/tool-use.md`.

## Next steps

- Need an agent loop, MCP servers, or built-in tools without writing the plumbing?
  When you outgrow hand-rolled `messages.create`, see **bot-brain-agent** — it layers
  the Claude Agent SDK behind the *same* `respond()` interface.
- Persist `history` across turns → **bot-session-state**.
- Screen inputs/outputs → **bot-safety**.

## References

- `references/tool-use.md` — full tool-use loop, the `@beta_tool` runner, tool_result
  error handling, model-id notes.
- `references/prompt-caching.md` — breakpoint placement, multi-turn caching, the
  silent-invalidator audit.
