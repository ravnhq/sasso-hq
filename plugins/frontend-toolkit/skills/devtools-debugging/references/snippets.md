# Live-page debugging sequences

MCP tool sequences for each workflow. Tool names grounded against
`/chromedevtools/chrome-devtools-mcp` (Context7) at authoring time. These are the
DevTools MCP tools you call in a session — not shell commands.

The shape is always the same: **navigate → reproduce → observe → (edit) → re-verify.**

## 1. Console error / uncaught exception

```
navigate_page         { url: "http://localhost:3000/checkout" }
# reproduce the exact trigger:
take_snapshot                                   # get element UIDs
click                 { uid: "<pay-button-uid>" }
list_console_messages { types: ["error"] }      # read the real exception + stack
```

Read the stack frame in the console output to find the source line — fix there,
then re-`navigate_page`, repeat the click, and confirm the error is gone. Use
`includePreservedMessages: true` if the error fires during a navigation and would
otherwise be cleared.

## 2. Failed or wrong network request

```
navigate_page         { url: "http://localhost:3000/orders" }
list_network_requests { resourceTypes: ["Fetch", "XHR"] }   # find the offender, note its reqid
get_network_request   { reqid: <reqid-from-the-list> }      # status, headers, body
```

Split the diagnosis from the response:

- **4xx / 5xx, or wrong body from the server** → server/contract bug. The client
  sent a request; the server answered wrong. Stop editing the component.
- **Request never sent, wrong URL, wrong params/headers** → client bug. Trace back
  to where the request is built.

Re-verify by reproducing the action and confirming the request now has the right
shape and a 2xx.

## 3. DOM / layout / styling bug

```
navigate_page    { url: "http://localhost:3000/profile" }
take_snapshot                                   # live DOM structure + element UIDs
take_screenshot                                 # what the user actually sees
take_screenshot  { uid: "<misrendered-uid>" }   # tighter shot of one element
```

`take_snapshot` tells you the structure is right (or wrong); `take_screenshot`
tells you the *pixels* are right (or wrong). A layout bug often has correct DOM and
wrong appearance — you need the screenshot to see it. For computed style or a
measured box, `evaluate_script` against the live element:

```
evaluate_script  { function: "() => { const el = document.querySelector('.card'); const s = getComputedStyle(el); return { display: s.display, width: s.width, position: s.position }; }" }
```

## 4. Performance regression (diagnose, then hand off)

```
navigate_page           { url: "http://localhost:3000/feed" }   # navigate BEFORE tracing
performance_start_trace { reload: true, autoStop: true }        # trace a fresh load
# (interact if the regression is on an interaction rather than load)
performance_stop_trace                                          # if not auto-stopped
# the trace result lists the bottleneck + the available insight sets and their ids;
# drill into a named one:
performance_analyze_insight  { insightName: "LCPBreakdown", insightSetId: "<id-from-trace>" }
```

This tells you **where the time goes** (LCP element, long task, layout shift). The
*fix* — code-splitting, render cost, reserving space for CLS — is
`frontend-performance`'s job; hand off there with the bottleneck in hand rather
than re-deriving the method.

## Driving interactions

To reproduce a bug you usually have to drive the UI. Always `take_snapshot` first
to get current UIDs (they're snapshot-scoped), then:

```
click       { uid: "<uid>" }
fill_form   { elements: [ { uid: "<user-uid>", value: "ada" }, { uid: "<pw-uid>", value: "secret" } ] }
```

Prefer `fill_form` over many single `fill` calls for forms — it's one reliable
call. Re-`take_snapshot` after the DOM changes; stale UIDs won't resolve.
