# Live-page debugging checklist

Run this against a frontend bug. It's ordered **reproduce-first** — don't skip to
the fix. Assumes the DevTools MCP is wired up (`setup.md`).

## Reproduce first
- [ ] Can you reproduce the bug in the running page (`navigate_page` + the exact interaction), not just describe it?
- [ ] Are you on a fresh, current build — not a stale bundle from before your last edit?
- [ ] If the bug needs auth, are you actually logged in (or attached to a real session, not `--isolated`'s clean profile)?
- [ ] Are you debugging headed for anything visual (headless can hide layout)?

## Observe the real signal
- [ ] Have you read the actual signal — console / network / DOM / screenshot — rather than inferring it from source?
- [ ] Console: any errors (`list_console_messages { types: ["error"] }`) tied to the repro, with their stack?
- [ ] Network: for a data bug, did you `get_network_request` the offender and read status + body — and decide client-bug vs server-bug from the response?
- [ ] Visual: did you `take_screenshot` (not just `take_snapshot`) to confirm what actually rendered?
- [ ] Does the page contradict the source? If so, the page wins — follow it.

## One hypothesis, one change
- [ ] Do you have a single hypothesis that explains the observed signal?
- [ ] Are you changing one thing, not several at once?
- [ ] (Discipline owned by `superpowers:systematic-debugging` — defer to it here.)

## Verify in the same page
- [ ] Did you reproduce the *same way* after the edit and confirm the signal changed?
- [ ] Did you re-snapshot before re-interacting (stale UIDs won't resolve)?
- [ ] Is the fix confirmed against the page, not assumed from the diff?

## Close out
- [ ] For a perf bug: did you stop at diagnosis and hand the bottleneck to `frontend-performance` for the fix?
- [ ] Did you capture the reproduced bug as a regression test (`frontend-testing`) so it can't silently come back?
