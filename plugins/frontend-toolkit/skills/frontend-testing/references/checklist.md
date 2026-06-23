# Frontend testing checklist

Run this against any test (or test file) you write or review.

## Behavior, not implementation
- [ ] Does every assertion check something the user can perceive (text, role, visible/enabled), not internal state, props, or "was this function called"?
- [ ] Would the test survive a refactor that preserves behavior (rename a hook, move state, swap a library)? If not, it's coupled to implementation.
- [ ] Is the test named after the behavior ("submits the form", "shows an error"), not the unit ("calls handleSubmit")?
- [ ] Are snapshots avoided except where a serialized blob is genuinely the contract? (They assert nothing meaningful and rot silently.)

## Queries (accessibility-first)
- [ ] Is each element found by role + accessible name first, then label, then visible text?
- [ ] Is `getByTestId` used only as an escape hatch, not as the default selector?
- [ ] No queries by CSS class, tag, or DOM structure (`container.querySelector`, `.firstChild`)?
- [ ] `getBy*` for things that must exist, `queryBy*` for asserting non-existence, `findBy*` for things that appear later — used deliberately, not interchangeably?

## Interaction
- [ ] Interactions go through `userEvent` (`const user = userEvent.setup()`), not raw `fireEvent`, unless there's a specific reason?
- [ ] Is every `user.*` call awaited?

## Async & network
- [ ] Is anything that appears asynchronously awaited via `findBy*`/`waitFor` rather than asserted synchronously?
- [ ] Are `waitFor` callbacks side-effect-free and limited to a single assertion (no interactions, no multiple unrelated checks inside)?
- [ ] Is the network mocked at the boundary (MSW handlers), not by stubbing `fetch` or mocking the module under test?
- [ ] Do happy-path handlers live in a shared file, with per-test error/edge states added via `server.use(...)` and reset in `afterEach`?
- [ ] Is the server configured to fail on unhandled requests (`onUnhandledRequest: "error"`) so a missing mock is loud, not silent?

## React Native parity (if applicable)
- [ ] Queries use RN-aware roles/labels (`getByRole`, `getByLabelText`) and matchers (`toBeOnTheScreen`), not web-only assumptions?
- [ ] Interactions use `user.press`/`user.type` from `@testing-library/react-native`?
- [ ] Are timers, animations, and debounced work driven deterministically (fake timers / advancing) rather than waited on by wall-clock?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (component shape → `component-design`, deep a11y audit → `accessibility-audit`, data/caching behavior → `data-fetching`, form validation rules → `forms-and-validation`.)
