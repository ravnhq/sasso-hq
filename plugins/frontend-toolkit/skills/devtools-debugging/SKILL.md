---
name: devtools-debugging
description: Debug frontend web issues against a live Chrome via the Chrome DevTools MCP instead of guessing from source — reproduce the bug in the running page, then read the real console, network, DOM, and performance signal. Use when a page throws a console error, a network request fails or returns the wrong data, layout or styling renders wrong, or an interaction janks, and when first wiring the DevTools MCP into a repo.
---

# DevTools debugging

Debug frontend issues by **observing the running page**, not by guessing from
source. The Chrome DevTools MCP drives a real Chrome, so the actual console
output, the actual response body, the actual computed style are available
directly — which is almost always faster and more correct than reading a
component and forming a theory. This skill wires that MCP up, then teaches a
reproduce-first loop and four concrete workflows on top of it.

**Web only.** The DevTools MCP drives Chrome, so this skill is for web. For React
Native, debug with the RN DevTools / Flipper instead — out of scope here.

**Version targets:** `chrome-devtools-mcp@latest`, current stable Chrome, Node ≥22.
Tool names and config grounded against Context7 (`/chromedevtools/chrome-devtools-mcp`)
at authoring time — see `references/snippets.md`.

## First time? Wire up the MCP

If `claude mcp list` doesn't show `chrome-devtools`, set it up before debugging —
**`references/setup.md`** has the runbook. The house default is **project scope**
(committed to the working repo so every frontend dev gets it) running `--isolated`
and headed. You only do this once per repo.

## The core loop

Debugging against a live page is a loop, not a guess: **reproduce in the running
page → observe the real signal (console / network / DOM / screenshot) → form one
hypothesis → change one thing → verify in the same page.** The discipline here —
reproduce before theorizing, change one variable at a time — is owned by
`superpowers:systematic-debugging`; this skill defers to it and adds only what's
unique to driving a live Chrome through the MCP.

The rule that makes it pay off: **trust the page over the source.** When the code
says one thing and the running page says another, the page is right. The whole
point of the MCP is to stop guessing — so read the signal before you edit.

## Principles

- **Reproduce first, in the real page.** `navigate_page` to where the bug lives and
  drive the exact interaction (`click`, `fill_form`) that triggers it before you
  theorize. A bug you can't reproduce in the page, you can't confirm you've fixed.
- **Read the signal, don't infer it.** The console (`list_console_messages`), the
  network (`list_network_requests` / `get_network_request`), the DOM
  (`take_snapshot`), and the rendered pixels (`take_screenshot`) are observable —
  look at them instead of reasoning about what the code "should" do.
- **Change one thing, then re-verify in the same page.** After an edit, reproduce
  the same way and confirm the signal changed. An unverified fix is a hypothesis.
- **Snapshot for structure, screenshot for appearance.** `take_snapshot` returns
  the accessible DOM text + element UIDs you act on; `take_screenshot` shows what
  the user actually sees. Layout and visual bugs need the screenshot — the DOM can
  be correct while the pixels are wrong.
- **Diagnose performance here, fix it there.** A `performance_start_trace` tells you
  *where* the time goes; the *fix* method (Core Web Vitals, bundle, render cost)
  lives in `frontend-performance`. Don't re-derive it.

## Workflows

Concrete MCP tool sequences for each, in **`references/snippets.md`**:

1. **Console error / uncaught exception** — navigate, reproduce, `list_console_messages`, trace to source.
2. **Failed or wrong network request** — `list_network_requests`, then `get_network_request` for the offender; read status/headers/body to split client bug from server bug.
3. **DOM / layout / styling bug** — `take_snapshot` for live structure + computed style, `take_screenshot` to confirm what actually rendered.
4. **Performance regression** — `performance_start_trace` (reload), read the bottleneck, then hand off to `frontend-performance` for the fix.

Deep React-internals / profiler debugging isn't a workflow here — the DevTools MCP
doesn't expose React DevTools cleanly. Use the browser React DevTools extension
directly for that.

## How to use this skill

1. Not wired up yet? Run **`references/setup.md`** once for the repo.
2. Run **`references/checklist.md`** against the bug — it's ordered reproduce-first.
3. Reach for the matching sequence in **`references/snippets.md`**.
4. Check **`references/pitfalls.md`** — the live-page traps that waste the most time.

## Related

- The debugging *discipline* (reproduce, isolate, one change at a time) → `superpowers:systematic-debugging`
- Fixing a performance bottleneck once a trace has found it → `frontend-performance`
- Capturing the reproduced bug as a regression test after the fix → `frontend-testing`
