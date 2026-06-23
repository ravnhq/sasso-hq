---
name: frontend-testing
description: Test React-family and React Native components and user flows by behavior, not implementation detail — accessible queries, real user interaction, async awaited honestly, and the network mocked at the boundary. Use when writing or reviewing component/integration tests, deciding what to assert, fixing flaky or brittle tests, or choosing what to mock.
---

# Frontend testing

Stack-agnostic principles, concrete examples in React 19 and React Native.
The tools differ across frameworks; the judgment — *test what the user
experiences, not how the code achieves it* — does not.

**Version targets:** React 19, React Native Testing Library 13 (current), MSW 2,
run under Vitest 3 or Jest 29+. Snippets grounded against Context7
(`/testing-library/testing-library-docs`, `/callstack/react-native-testing-library`,
`/mswjs/mswjs.io`) at authoring time — see `references/snippets.md`.

## The core question

Every test decision reduces to: *would this test still pass after a refactor
that changes the implementation but not what the user sees?* If a
behavior-preserving refactor breaks the test, the test is coupled to
implementation — it will cost you maintenance without buying confidence. Assert
on the rendered, accessible result; never on internal state, props, or which
function got called inside the component.

## Principles

- **Test behavior, not implementation.** Assert what the user perceives —
  visible text, roles, enabled/disabled, what appears after a click. Reaching
  for component state, instance methods, or "was this hook called" is the smell
  that you're testing the mechanism instead of the outcome.
- **Query the way users find things.** Prefer role + accessible name, then
  label, then visible text. `getByTestId` is an escape hatch for when nothing
  user-facing identifies the node — not the default. Accessible queries double
  as a free accessibility check: if the test can't find the button by its role
  and name, neither can a screen reader.
- **Interact like a user.** Drive interactions with `user-event`
  (`userEvent.setup()`), which fires the full sequence a real interaction emits
  (focus, keydown, input, click). Raw `fireEvent` dispatches one synthetic event
  and skips the rest, so it can pass when the real app would fail.
- **Handle async honestly.** UI that appears after a tick is awaited with
  `findBy*` or `waitFor`; never assert synchronously right after an async update.
  Unhandled async is the leading cause of `act()` warnings and flaky tests.
- **Mock at the boundary, not the unit.** Mock the *network* (MSW) and leave your
  components, hooks, and store real. Mocking the module under test, or stubbing
  `fetch` by hand, tests the mock instead of the code.
- **Mobile parity.** The same rules hold in React Native Testing Library; the
  difference is primitives and matchers (`getByRole`/`user.press`,
  `toBeOnTheScreen`) and that you must drive timers/animations deterministically.
  See `references/pitfalls.md`.

## How to use this skill

1. Run **`references/checklist.md`** against the test (or test file) you're writing or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (behavior-first component test,
   user flow, network mocked at the boundary, React Native parity).
3. Check **`references/pitfalls.md`** before you ship — most brittle/flaky tests hit at least one.

## Related

- Designing the component you're testing → `component-design`
- Auditing accessibility against WCAG (beyond what queries catch) → `accessibility-audit`
- Testing data loading/caching → `data-fetching`
- Testing form validation → `forms-and-validation`
- Profiling instead of asserting on perf → `frontend-performance` / `native-performance`
