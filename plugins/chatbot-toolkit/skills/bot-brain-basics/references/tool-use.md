# Tool use — the full loop

For the conceptual quick version, see `SKILL.md` § Adding tools. This file is the
runnable detail.

## Defining tools (raw JSON schema)

```python
tools = [{
    "name": "get_order_status",
    "description": "Look up the status of a customer order. "
                   "Call this when the user asks where their order is.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string", "description": "The order id"}},
        "required": ["order_id"],
    },
}]
```

Be prescriptive about *when* to call the tool in the description — recent Claude
models reach for tools conservatively, and a clear trigger condition lifts the
should-call rate.

## Manual loop inside `respond()`

```python
async def respond(self, history: list[Message], incoming: str) -> str:
    messages = [{"role": m.role, "content": m.text} for m in history]
    messages.append({"role": "user", "content": incoming})

    while True:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
        )
        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")

        # pause_turn: a server-side tool hit its iteration limit — re-send to resume
        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continue

        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = await run_tool(block.name, block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})
```

Invariants:

- Append the full `response.content` (not just text) as the assistant turn before
  the results — the API needs the `tool_use` blocks present.
- One `tool_result` per `tool_use`, each with the matching `tool_use_id`.
- `block.input` is already parsed — use it as a dict; don't regex the JSON.

## Tool errors

Report failures back so Claude can adapt instead of crashing the loop:

```python
{"type": "tool_result", "tool_use_id": block.id,
 "content": "Order id not found. Ask the user to re-check it.",
 "is_error": True}
```

## The SDK tool runner (when you don't need to gate)

```python
from anthropic import beta_tool

@beta_tool
def get_order_status(order_id: str) -> str:
    """Look up the status of a customer order.

    Args:
        order_id: The order id.
    """
    return lookup(order_id)

runner = client.beta.messages.tool_runner(
    model="claude-haiku-4-5", max_tokens=1024,
    tools=[get_order_status],
    messages=[{"role": "user", "content": incoming}],
)
for message in runner:        # loop runs automatically; async via @beta_async_tool
    ...
```

The runner generates the schema from the signature and runs the call→execute→feed
loop for you. Reach for the manual loop instead when you need human-in-the-loop
approval, custom logging, or conditional execution.

## Tool choice

```python
tool_choice={"type": "auto"}                       # default — Claude decides
tool_choice={"type": "any"}                        # must use some tool
tool_choice={"type": "tool", "name": "get_order_status"}   # force this one
```

## Model-id notes

Current ids: `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`.

On Opus 4.8 / 4.7 the request surface is stricter: `temperature`/`top_p`/`top_k`
and `thinking={"type": "enabled", "budget_tokens": N}` all return 400. Use
`thinking={"type": "adaptive"}` and steer with the prompt. Haiku and Sonnet 4.6 do
not accept `effort`. For a customer-facing chat Brain, Haiku or Sonnet is usually
the right default — reach for Opus only when the task needs the extra reasoning.
