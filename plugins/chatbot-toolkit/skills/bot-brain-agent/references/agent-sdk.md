# Claude Agent SDK — reference

Verified against the official Python Agent SDK reference (code.claude.com /
platform.claude.com, current as of this writing) and the
`anthropics/claude-agent-sdk-python` repo. Package name and entry points confirmed —
not guessed.

## Package

```bash
pip install claude-agent-sdk
```

```python
from claude_agent_sdk import (
    query,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    PermissionResultAllow,
    PermissionResultDeny,
)
```

## `query()` — one-shot

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful support assistant.",
        max_turns=4,
    )
    async for message in query(prompt="Where is order 1234?", options=options):
        print(message)

asyncio.run(main())
```

Signature (shape):
`async def query(*, prompt: str | AsyncIterable[dict], options: ClaudeAgentOptions | None = None, transport=None) -> AsyncIterator[Message]`.

Creates a new session by default; no history retained unless
`continue_conversation=True` or `resume=<session_id>` is set.

## `ClaudeSDKClient` — multi-turn

```python
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async with ClaudeSDKClient(options=options) as client:
    await client.query("What's the capital of France?")
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

    await client.query("And its population?")     # same session, retains context
    async for message in client.receive_response():
        ...
```

- `receive_response()` yields messages until a `ResultMessage`.
- Same session id across `query()` calls; prior turns are available to Claude.
- Supports `interrupt()`; explicit lifecycle via the async context manager (or
  `connect()` / `disconnect()`).

## `ClaudeAgentOptions` — the knobs that matter for a bot

| Option | Use |
|---|---|
| `system_prompt` | the bot's persona/instructions |
| `mcp_servers` | `{name: server}` — in-process and external MCP servers |
| `allowed_tools` | allowlist, e.g. `["mcp__orders__get_order_status"]` |
| `can_use_tool` | async permission handler — gate each call |
| `max_turns` | bound the agent loop per turn |
| `max_budget_usd` | stop when the cost estimate is reached |
| `permission_mode` | e.g. `"acceptEdits"` for file-editing agents |
| `cwd` | working directory for file/bash tools |
| `resume` / `continue_conversation` | pick a prior session back up |
| `setting_sources` | load Skills from the filesystem |

## In-process tools

```python
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}

calculator = create_sdk_mcp_server(name="calc", version="1.0.0", tools=[add])

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add"],
)
```

`@tool(name, description, input_schema)` — `input_schema` is a simple
`{field: type}` map or a full JSON Schema. The decorated function returns
`{"content": [...]}`. `create_sdk_mcp_server` bundles them into an in-process MCP
server (no subprocess, no network). Tools are addressed `mcp__<server>__<tool>`.

## External MCP servers

The same `mcp_servers` option also takes external (subprocess/URL) MCP servers, so
a bot can reach GitHub, a database, or internal APIs. Their tools surface under the
same `mcp__<server>__<tool>` naming and are allowlisted via `allowed_tools`. For the
exact config shape of subprocess vs. URL servers, consult the current Agent SDK
reference — the surface evolves.

## Permission gating

```python
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny

async def can_use_tool(tool_name, input_data, context):
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/etc/"):
        return PermissionResultDeny(message="System path write blocked")
    return PermissionResultAllow(updated_input=input_data)

options = ClaudeAgentOptions(can_use_tool=can_use_tool, allowed_tools=["Read", "Write"])
```

This is the agent-loop equivalent of the human-in-the-loop you'd hand-code in a raw
`messages.create` tool loop.

## Context management

The SDK persists the session and Claude Code applies server-side **compaction** as
context fills (the raw API exposes this via the `compact-2026-01-12` beta). Bound
runaway loops with `max_turns` and `max_budget_usd`; resume long conversations with
`resume`. The Agent SDK reference does not document a separate manual-compaction
knob in the Python surface — rely on the managed behavior plus the bounds above. For
the raw-API compaction mechanics (append `response.content`, not just text), see the
**bot-brain-basics** references.

## `query()` vs `ClaudeSDKClient`

| | `query()` | `ClaudeSDKClient` |
|---|---|---|
| session | new each call | one persistent session |
| history | fresh start | retained across `query()` |
| interrupts | no | yes (`interrupt()`) |
| custom tools | yes | yes |
| fits a bot Brain | one-off replies | multi-turn chat ← prefer this |
