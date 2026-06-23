# Forms and validation checklist

Run this against any form you build or review.

## State & ownership
- [ ] Is form state owned by a library/platform (React Hook Form, React 19 action), not a pile of per-field `useState`?
- [ ] Is there one schema as the source of truth, with the type inferred from it (`z.infer`) — not declared twice?
- [ ] Are `defaultValues` set so every field is controlled from first render (no undefined → defined warning)?

## Validation
- [ ] Does validation run on blur or submit (not on every keystroke), then re-validate on change after a field errors?
- [ ] Are messages specific and actionable ("Enter a valid email", not "Invalid")?
- [ ] Is the same schema re-validated on the server? (Client validation is never the contract.)

## Accessibility
- [ ] Does every control have a programmatic label (`<label htmlFor>` / `accessibilityLabel`) — not a placeholder standing in for one?
- [ ] Is `aria-invalid` set on errored controls, and the message linked via `aria-describedby`?
- [ ] Is the error announced (`role="alert"`), and is focus moved to the first error on failed submit?
- [ ] Are required fields conveyed to assistive tech (not by colour alone)?

## Submission
- [ ] Is the submit button disabled while submitting, and double-submit prevented?
- [ ] Is there a visible pending state (`isSubmitting` / `useFormStatus().pending`)?
- [ ] Are server-side errors surfaced in the same place as field errors?
- [ ] On success, is the form reset or the user navigated — deliberately, not by accident?

## React Native parity (if applicable)
- [ ] Are inputs driven by `Controller` (or equivalent) against the same schema?
- [ ] Is `keyboardType`/`inputMode` set per field, with `returnKeyType` + focus-next wiring?
- [ ] Does a `KeyboardAvoidingView` (or keyboard-aware scroll) keep the active field visible?
- [ ] Does every `TextInput` have an `accessibilityLabel`, and `autoComplete`/`textContentType` for autofill?

## Reuse / boundaries
- [ ] Is cross-field or app-wide state a `state-management` concern, not stuffed into the form?
- [ ] Is the network submit a `data-fetching` concern (loading/error/caching), not re-implemented here?
