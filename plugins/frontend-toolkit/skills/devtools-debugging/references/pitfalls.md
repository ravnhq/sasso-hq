# Live-page debugging pitfalls

The traps that waste the most time when debugging through the DevTools MCP.

## Debugging a stale build

You edited source, but the page still runs the old bundle — so the "bug" you're
still seeing is a ghost, and the "fix" you think failed actually worked. Confirm
the dev server recompiled (or hard-reload) **before** you re-read the signal. When
in doubt, `navigate_page` fresh rather than trusting hot-reload to have applied.

## `--isolated` dropped your auth session

`--isolated` starts from a clean, cookieless profile every session — great for
not polluting your real browser, but it means you're logged out. A bug that only
reproduces behind auth won't appear, and you'll chase the wrong thing. Either log
in within the session as part of the repro, or attach to a real logged-in browser
with `--browserUrl` / `--wsEndpoint` instead of `--isolated` (see `setup.md`).

## Headless hid a visual bug

Running `--headless` (or in CI) can render layout differently from a headed
browser, and you can't *see* the result. Visual and layout bugs need eyes on the
pixels — debug those headed and use `take_screenshot`. Treat a headless "looks
fine" as unconfirmed for anything visual.

## Trusting the source over the page

The whole point of the MCP is to stop guessing — but it's easy to glance at the
console, jump to a theory from the code, and edit without actually confirming the
theory against the page. When source and page disagree, the page wins. Read the
real signal, and re-read it after the edit.

## Stale snapshot UIDs

Element UIDs come from a `take_snapshot` and are scoped to that snapshot. After the
DOM changes — a click, a route change, new data — old UIDs won't resolve. Re-snap
before interacting again rather than reusing UIDs from before the change.

## Snapshot looked right, but it rendered wrong

`take_snapshot` shows DOM structure and accessible text; it does **not** show
appearance. A node can be present and correct in the snapshot while overlapped,
clipped, off-screen, or mis-styled in the actual render. For anything layout- or
style-shaped, confirm with `take_screenshot`, not the snapshot alone.

## Fixing performance here instead of handing off

`performance_start_trace` is for *finding* the bottleneck. It's tempting to start
optimizing in the same breath — but the fix method (Core Web Vitals targets,
bundle splitting, render cost) belongs in `frontend-performance`. Diagnose here,
fix there; don't re-derive the loop.

## Console errors from before the repro

By default `list_console_messages` is scoped to the current page since the last
navigation — but earlier errors, or errors that fire across a navigation, can
mislead. Reproduce cleanly, and reach for `types: ["error"]` to cut noise and
`includePreservedMessages: true` only when the error spans a navigation.
