---
name: bot-brain-agent
description: Teach the Claude Agent SDK (claude-agent-sdk) and how to layer it behind the reference app's Brain interface — the agent loop, in-process tools, MCP, and context management. Use when a bot needs an agent that runs tools/files/MCP autonomously, when outgrowing a hand-rolled messages.create loop, or when upgrading ClaudeBrain without changing respond().
---

# Bot Brain Agent — the Claude Agent SDK

The recommended upgrade path for a bot's brain. The reference app ships a `Brain`
built on the raw Messages API (one `messages.create` call behind
`respond()` — see **bot-brain-basics**). When the bot needs to *act* — run tools
across turns, read files, call MCP servers, manage a long context — you swap the
implementation for the **Claude Agent SDK** while keeping the **same interface**.

That through-line is the whole point: `reference-app/app/brain.py` defines

    class Brain(Protocol):
        async def respond(self, history: list[Message], incoming: str) -> str: ...

Nothing downstream (`Channel`, `SessionStore`, the webhook glue) knows or cares
whether `respond()` is one `messages.create` call or a full agent loop. You upgrade
the engine without touching the chassis.

## Package and entry points

```bash
pip install claude-agent-sdk        # the package is "claude-agent-sdk"
```

```python
from claude_agent_sdk import (
    query,                 # one-shot: async iterator of messages
    ClaudeSDKClient,       # multi-turn: holds a session, supports interrupts
    ClaudeAgentOptions,    # config: system prompt, tools, mcp_servers, limits
    tool,                  # @tool decorator for in-process tools
    create_sdk_mcp_server, # bundle @tool functions into an in-process MCP server
)
```

Two surfaces:

- `query(prompt=..., options=...)` — a single exchange, returns
  `AsyncIterator[Message]`. Good for stateless request/reply.
- `ClaudeSDKClient` — keeps a session across multiple `query()` calls, retains
  history, and supports `interrupt()`. This is the one that fits a bot Brain.

## Layering it behind `respond()`

A `ClaudeBrain` rewritten on the Agent SDK, with the interface unchanged:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

class AgentBrain:
    def __init__(self, model: str, options: ClaudeAgentOptions) -> None:
        self._options = options

    async def respond(self, history: list[Message], incoming: str) -> str:
        async with ClaudeSDKClient(options=self._options) as client:
            await _replay(client, history)        # feed prior turns
            await client.query(incoming)
            parts = []
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    parts.extend(b.text for b in message.content
                                 if isinstance(b, TextBlock))
            return "".join(parts)
```

Same signature, same return type. `SessionStore` still owns `history`; the Brain
just drives a richer engine. `receive_response()` yields messages until the turn's
`ResultMessage`.

## The agent loop — handled for you

This is the upgrade over the raw SDK. You don't write the call→run-tool→feed-result
loop yourself; the SDK runs it:

1. Claude emits a `ToolUseBlock`.
2. The SDK executes the tool (an in-process `@tool` or an MCP server tool).
3. The result returns to Claude.
4. Claude reasons and continues, or finishes with a `ResultMessage`.

Bound it with `ClaudeAgentOptions(max_turns=..., max_budget_usd=...)`. Gate
individual tool calls with a `can_use_tool` permission handler (return
`PermissionResultAllow` / `PermissionResultDeny`) — the agent equivalent of the
human-in-the-loop you'd hand-roll in the raw loop.

## In-process tools

Define tools as plain async functions, bundle them, attach via options:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("get_order_status", "Look up an order's status", {"order_id": str})
async def get_order_status(args):
    return {"content": [{"type": "text", "text": lookup(args["order_id"])}]}

server = create_sdk_mcp_server(name="orders", version="1.0.0",
                              tools=[get_order_status])

options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"orders": server},
    allowed_tools=["mcp__orders__get_order_status"],
)
```

In-process tools run in the same process as the bot — no subprocess, no network.
Tool names are scoped `mcp__<server>__<tool>`.

## MCP — external capabilities

Beyond in-process tools, attach external MCP servers (GitHub, a database, internal
APIs) through the same `mcp_servers` option. The SDK manages the connection and
surfaces the server's tools to the agent under the `mcp__<server>__<tool>` naming.
This is how a bot Brain gains real-world reach without you wiring each integration
by hand. See `references/agent-sdk.md`.

## Context management

A long-running chat eventually outgrows the context window. The Agent SDK manages
the running session for you — and Claude Code's server-side **compaction**
summarizes earlier context as the window fills (the underlying API exposes this via
the `compact-2026-01-12` beta on the raw SDK). Practical levers on
`ClaudeAgentOptions`: `max_turns` to bound a turn, `max_budget_usd` to bound cost,
and `resume`/`continue_conversation` to pick a session back up. For the raw-API
compaction mechanics, see **bot-brain-basics**' references.

## Model ids

Current Claude 4.x: `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`. An
agent doing multi-step tool work benefits from Sonnet or Opus; set the model on the
options/client.

## Next steps

- For the raw `messages.create` fundamentals this builds on — the tool-use loop by
  hand, streaming, prompt caching — see **bot-brain-basics**.
- Persist session history across turns → **bot-session-state**.
- Screen agent inputs/outputs → **bot-safety**.

## References

- `references/agent-sdk.md` — `query` vs `ClaudeSDKClient`, full options reference,
  MCP server wiring, permission handlers, and the verified package facts.
