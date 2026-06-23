# Frontend testing pitfalls

## Testing implementation details
**Symptom:** assertions read component state, spy on internal handlers, or check
"was `useFoo` called" — and the test breaks every time you refactor without
changing behavior.
**Fix:** assert on what the user perceives — rendered text, roles, visible/enabled.
If the only way to verify something is to reach inside, the behavior probably
isn't observable and the test isn't worth its upkeep.

## Querying by test id (or class) first
**Symptom:** `getByTestId` everywhere, or `container.querySelector(".btn")`.
**Fix:** query by role + accessible name, then label, then visible text;
`getByTestId` is the escape hatch for nodes with no user-facing identity. A query
that can't find the element accessibly is also telling you a screen reader can't.

## fireEvent for everything
**Symptom:** `fireEvent.click` / `fireEvent.change` drive the whole test; it passes
but the real app misbehaves (or vice-versa).
**Fix:** use `userEvent` (`const user = userEvent.setup()`), which dispatches the
full event sequence a real interaction emits (focus, keydown, input, click).
Reserve `fireEvent` for low-level events `user-event` doesn't model.

## Not awaiting async
**Symptom:** `act(...)` warnings, intermittent failures, assertions that run before
the UI updates.
**Fix:** `await` every `user.*` call and use `findBy*`/`waitFor` for anything that
appears after a tick. Never assert synchronously straight after triggering async work.

## Mocking the unit under test (or stubbing fetch)
**Symptom:** `vi.mock("./UserCard")`, or hand-stubbed `global.fetch`, so the test
exercises the mock rather than the code.
**Fix:** mock at the network boundary with MSW (`http`/`HttpResponse`) and keep
components, hooks, and store real. Set `onUnhandledRequest: "error"` so a missing
handler fails loudly instead of silently hitting the real network.

## Snapshot overuse
**Symptom:** `toMatchSnapshot()` is the assertion; reviewers rubber-stamp `-u`
updates and the snapshot stops meaning anything.
**Fix:** assert specific, accessible outcomes. Keep snapshots for the rare case
where a serialized blob genuinely *is* the contract (e.g. a generated payload).

## waitFor doing too much
**Symptom:** interactions or several unrelated assertions stuffed inside a single
`waitFor` callback, which then retries side effects.
**Fix:** keep `waitFor` callbacks side-effect-free and down to one assertion;
prefer `findBy*` for "wait until it's there". Put interactions before the wait.

## RN: web assumptions and undriven time
**Symptom:** web-only queries/matchers in React Native tests, or flaky tests that
wait on real animation/debounce timers.
**Fix:** query with RNTL roles/labels and matchers (`toBeOnTheScreen`), interact
with `user.press`/`user.type`, and advance fake timers deterministically instead
of waiting on the wall clock.
