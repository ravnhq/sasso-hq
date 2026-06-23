# Wiring up the Chrome DevTools MCP

One-time setup per repo. Config grounded against
`/chromedevtools/chrome-devtools-mcp` (Context7) at authoring time.

## Prerequisites

- **Node ≥22** (`node -v`) — the server runs via `npx`.
- **A current stable Chrome** installed. The server downloads/launches its own
  Chrome by default; `--channel` or `--executablePath` point it at a specific one.

## Project scope (house default)

Debugging this way is the team default for a frontend repo, so wire the MCP at
**project scope** — it lands in a committed `.mcp.json` at the repo root, and
everyone who clones the repo gets it. Run this **in the consuming frontend repo**
(not in a plugins repo):

```shell
claude mcp add --scope project chrome-devtools \
  -- npx -y chrome-devtools-mcp@latest --isolated
```

That writes:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--isolated"]
    }
  }
}
```

Commit `.mcp.json`. `--isolated` runs each session in a throwaway profile so
debugging never pollutes — or leaks — your real browser state. The server runs
**headed** by default (it only goes headless when you pass `--headless`), which is
what you want: you're debugging, so seeing the page is the point.

## Variants

- **User level** (personal, every repo, not committed) — drop `--scope project`:
  ```shell
  claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --isolated
  ```
- **Headless** (CI / non-interactive) — add `--headless`. Note the trade-off in
  `pitfalls.md`: headless can mask layout and visual bugs.
  ```shell
  claude mcp add --scope project chrome-devtools \
    -- npx -y chrome-devtools-mcp@latest --isolated --headless
  ```
- **Pin a Chrome channel** — `--channel=stable|beta|canary`, or point at a binary
  with `--executablePath=/path/to/chrome`.
- **Attach to your own Chrome** instead of launching one — `--browserUrl` /
  `--wsEndpoint` (or `--autoConnect`). Useful when the bug needs a real logged-in
  session; you lose `--isolated`'s clean profile in exchange (see `pitfalls.md`).

The full flag list lives in the upstream README — this covers the baseline plus
the knobs you'll actually reach for.

## Verify

```shell
claude mcp list
```

`chrome-devtools` should appear and report connected. In a session, the
`navigate_page`, `take_snapshot`, `list_console_messages`, etc. tools are then
available. A quick smoke test: `navigate_page` to any URL and `take_screenshot`.

## Troubleshooting

- **Not listed after `add`** — confirm you ran it in the intended repo (project
  scope is per-repo) and that `.mcp.json` was written at the repo root.
- **Connects but no tools fire** — the first `npx` run downloads the server and
  possibly Chrome; give it a moment, then retry. Check `node -v` is ≥22.
- **Launch fails / no Chrome** — install a stable Chrome, or pass
  `--executablePath` / `--channel` to point at an existing one.
- **Need a logged-in session** — `--isolated` starts cookieless by design. Either
  log in within the session, or attach to your real browser with `--browserUrl` /
  `--wsEndpoint` instead of `--isolated`.
