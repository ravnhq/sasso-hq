# Forms and validation pitfalls

## Validating on every keystroke
**Symptom:** errors flash while the user is still typing the first characters; the
form feels hostile.
**Fix:** validate on blur or submit (`mode: "onTouched"` / `"onBlur"` in React Hook
Form), then re-validate on change *after* a field has errored — immediate feedback
only once the user has left the field.

## Inputs with no programmatic label
**Symptom:** a placeholder stands in for a label; screen readers announce an
unlabelled edit field, and the hint vanishes the moment the user types.
**Fix:** every control gets a real `<label htmlFor>` (web) or `accessibilityLabel`
(RN). Placeholders are hints, not labels.

## Error text not linked to its input
**Symptom:** an error renders visually beside the field but isn't associated, so
assistive tech never connects the two.
**Fix:** set `aria-invalid` on the control, point `aria-describedby` at the message's
`id`, and give the message `role="alert"` so it's announced.

## Trusting client validation
**Symptom:** validation lives only in the browser; a crafted request bypasses every rule.
**Fix:** client validation is UX. Re-run the *same schema* on the server
(`schema.safeParse`) and treat its result as the contract.

## Duplicated validation rules
**Symptom:** "min 8 chars" is written in the input attribute, a hand-rolled check,
and the backend — and they drift apart over time.
**Fix:** one schema (Zod) as the source of truth; infer the type with `z.infer`;
import the same schema on client and server.

## Uncontrolled-to-controlled input warning
**Symptom:** React warns "changing an uncontrolled input to be controlled"; a field's
`value` starts as `undefined`.
**Fix:** provide `defaultValues` for every field (React Hook Form) or initialise state
so `value` is defined from the first render.

## Double submission
**Symptom:** impatient users double-tap submit and create two records.
**Fix:** disable submit while pending (`isSubmitting` / `useFormStatus().pending`) and
guard the handler against re-entry.

## RN: the keyboard covers the active field
**Symptom:** on mobile the on-screen keyboard hides the input being typed into.
**Fix:** wrap the form in `KeyboardAvoidingView` (with the right `behavior` per
platform) or a keyboard-aware scroll view, and wire `returnKeyType` + `onSubmitEditing`
to move focus between fields.

## RN: wrong keyboard and no autofill
**Symptom:** an email field shows the default alphabetic keyboard with
auto-capitalisation, fighting the user; nothing autofills.
**Fix:** set `keyboardType="email-address"` (or `inputMode="email"`),
`autoCapitalize="none"`, and `autoComplete`/`textContentType` so the platform can autofill.
