# Accessibility audit pitfalls

## Clickable `div`/`span`
**Symptom:** `<div onClick={...}>` for a button or link — no keyboard focus, no
role, no Enter/Space handling.
**Fix:** use a real `<button>` or `<a href>` (RN: `Pressable` with
`accessibilityRole`). If you truly can't, you owe `role`, `tabIndex={0}`, and key
handlers — but you almost never can't.

## Placeholder used as the label
**Symptom:** an input with only a `placeholder`; the name vanishes once the user
types, and some screen readers never announce it.
**Fix:** a persistent `<label htmlFor>` (or `accessibilityLabel`). Placeholders
are example text, not labels (3.3.2).

## Focus outline removed
**Symptom:** `outline: none` (or a CSS reset) with no replacement — keyboard users
can't see where they are.
**Fix:** keep a visible focus style; use `:focus-visible` to scope it to keyboard
use. Never remove it outright (2.4.7).

## Icon-only control with no accessible name
**Symptom:** a button or pressable whose only child is an icon; AT announces
"button" with no purpose.
**Fix:** add `aria-label`/`accessibilityLabel` and hide the glyph
(`aria-hidden="true"` / `importantForAccessibility="no"`) (4.1.2).

## Color or contrast failures
**Symptom:** status shown only by color (red = error), or text under 4.5:1 (3:1
for UI/large text).
**Fix:** pair color with text or an icon (1.4.1); check contrast and fix the
token, not the one instance (1.4.3, 1.4.11). Contrast belongs to `styling-systems`.

## Bad or redundant ARIA
**Symptom:** `role="button"` on a `<button>`, an `aria-label` that overrides the
visible text with something different, or `aria-*` that points at nothing.
**Fix:** prefer native semantics; reach for ARIA only when there's no element for
the job, and keep the accessible name matching the visible label. *No ARIA is
better than bad ARIA.*

## Focus left unmanaged
**Symptom:** opening a modal leaves focus behind it; closing it drops focus to the
top of the page; an SPA route change doesn't move focus at all.
**Fix:** move focus into the new context, restore it to the trigger on close, and
**trap Tab inside a modal** so it can't reach the page behind (2.4.3, 2.1.2). See
the dialog snippet.

## RN: tiny targets, missing roles, ungrouped rows
**Symptom:** taps miss small controls; custom toggles announce nothing useful; a
list row reads as several disconnected `Text` nodes.
**Fix:** size targets to ≥ 44pt/48dp (or add `hitSlop`); set `accessibilityRole`
+ `accessibilityLabel` + `accessibilityState` on interactive nodes; wrap rows in
`accessible` with one combined label (2.5.8, 4.1.2).

## Motion that ignores reduced-motion
**Symptom:** parallax, auto-playing, or large transition animations regardless of
the user's "reduce motion" setting — a vestibular-discomfort trigger.
**Fix:** gate non-essential motion behind `prefers-reduced-motion` (web) or
`AccessibilityInfo.isReduceMotionEnabled()` (RN); fall back to an instant or
fade change. This is shared ground with `animation-and-motion`.
