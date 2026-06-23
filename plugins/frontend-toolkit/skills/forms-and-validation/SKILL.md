---
name: forms-and-validation
description: Build accessible, well-validated forms in React-family web and React Native without reinventing the wheel — schema-driven validation, when validation runs, accessible errors, submission state, and mobile inputs. Use when building or reviewing a form, choosing a form/validation library, wiring client + server validation, or fixing form accessibility.
---

# Forms and validation

Stack-agnostic principles, concrete examples in React 19 (with React Hook Form +
Zod) and React Native. The examples port to Vue/Svelte; the judgments don't change.

**Version targets:** React 19, React Hook Form 7, Zod 4, React Native 0.81 (current
stable). Snippets grounded against Context7 (`/reactjs/react.dev`,
`/react-hook-form/documentation`, `/react-hook-form/resolvers`, `/websites/zod_dev_v4`,
`/facebook/react-native`) at authoring time — see `references/snippets.md`.

## The core question

Every form decision reduces to three questions: *where does each field's value live,
when does validation run, and how does an error reach the user?* Answer those and
submission, accessibility, and mobile parity follow. Most form bugs are one of the
three answered by accident.

## Principles

- **Don't hand-roll form state.** A library (React Hook Form) or the platform
  (React 19 form actions) already solves registration, dirty/touched tracking, and
  submission. A pile of `useState` per field re-implements that — worse, and untested.
- **One schema is the source of truth.** Define the shape and rules once (Zod),
  infer the TypeScript type from it (`z.infer`), validate the client with it, and
  re-validate *the same schema* on the server. Rules duplicated across input
  attributes, a hand check, and the backend will drift.
- **Validate at the right moment.** Validating on every keystroke punishes users
  mid-word; validating only on submit hides errors too long. Validate on blur or
  submit, then re-validate on change *once a field has errored*.
- **Every field is labelled; every error is announced.** A `<label htmlFor>` (web)
  or `accessibilityLabel` (RN), `aria-invalid` on the control, and the message tied
  back via `aria-describedby` with `role="alert"`. Unlabelled inputs and orphaned
  error text are the most common form a11y failures.
- **Submission is a state machine, not a function call.** idle → submitting →
  success | error. Disable submit while pending, prevent double-submit, surface
  server errors where field errors live, and move focus to the first error.
- **Client validation is UX; server validation is the contract.** The client check
  is for fast feedback. Never trust it — re-run the schema on the server. The network
  call itself is a `data-fetching` concern.
- **Mobile parity.** React Native has no `<form>` element and no HTML constraint
  validation, but the same schema and the same library (`Controller`) drive
  `TextInput`. The differences are primitives, `keyboardType`/`returnKeyType`, focus
  between fields, and keeping the keyboard off the active input. See `references/pitfalls.md`.

## How to use this skill

1. Run **`references/checklist.md`** against the form you're building or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (React Hook Form + Zod,
   React 19 form action, one schema on both sides, React Native form).
3. Check **`references/pitfalls.md`** before you ship — most form PRs hit at least one.

## Related

- Cross-field or app-wide state → `state-management`
- Submitting to a server, caching, retries → `data-fetching`
- A deeper a11y pass (focus order, screen-reader flows) → `accessibility-audit`
- Testing the form by behavior → `frontend-testing`
- Styling inputs and error states → `styling-systems`
