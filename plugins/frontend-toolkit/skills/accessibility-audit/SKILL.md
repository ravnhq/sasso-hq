---
name: accessibility-audit
description: Audit and fix accessibility (a11y) issues against WCAG 2.2 AA across React-family web and React Native — semantics, keyboard, focus, accessible names, contrast, and motion. Use when auditing a UI for accessibility, fixing a11y bugs, adding ARIA or focus management, reviewing for WCAG compliance, or making components usable with a screen reader and keyboard.
---

# Accessibility audit

Stack-agnostic principles, concrete examples in React 19 and React Native.
The standard is WCAG; the examples port to Vue/Svelte and native — the criteria don't change.

**Version targets:** React 19, React Native 0.81 (current stable); audited against
**WCAG 2.2 Level AA**. Snippets grounded against Context7 (`/reactjs/react.dev`,
`/facebook/react-native`) at authoring time — see `references/snippets.md`.

## The core question

Every accessibility decision reduces to: *can someone who doesn't see, hear, or
use a mouse the way you do still perceive, operate, and understand this?* If a
feature only works with sight, a pointer, or a steady hand, it isn't done.

## Principles

WCAG groups everything under four headings — content must be **P**erceivable,
**O**perable, **U**nderstandable, and **R**obust (POUR). In practice:

- **Semantics first, ARIA last.** A real `<button>`, `<a href>`, `<label>`, or RN
  `accessibilityRole` gives you a role, a name, focus, and keyboard handling for
  free. ARIA only *describes* — it never adds behavior. *No ARIA is better than
  bad ARIA.*
- **Everything operable by keyboard.** Every interactive element must be reachable
  and actionable with Tab/Enter/Space/arrows, with a visible focus indicator. A
  `div` with `onClick` is none of those.
- **Every control has an accessible name.** Icon-only buttons, inputs, and images
  need a name assistive tech can announce (a visible `<label>`, `aria-label`,
  `accessibilityLabel`, or `alt`). Decorative images get an *empty* name so they're skipped.
- **Don't lean on color or sense alone.** Color, shape, or position can't be the
  only signal — pair them with text or an icon. Body text needs ≥ 4.5:1 contrast
  (≥ 3:1 for large text and for UI/graphics).
- **Manage focus across state changes.** Opening a dialog moves focus in and traps
  it; closing restores it to the trigger. Route changes move focus to the new
  heading. Never strand focus on a hidden element.
- **Announce what changes silently.** Async results, validation errors, and toasts
  must reach assistive tech via a live region (`aria-live`) or RN
  `AccessibilityInfo.announceForAccessibility`.
- **Respect motion and motor needs.** Honor the reduced-motion setting, and size
  touch/click targets ≥ 24×24 CSS px (WCAG 2.5.8) — 44pt iOS / 48dp Android in practice.
- **Mobile parity.** The same criteria hold in React Native; the difference is
  primitives — `accessibilityRole`/`accessibilityLabel`/`accessibilityState`
  instead of HTML and ARIA. See `references/pitfalls.md`.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — a contrast or focus-state comparison — render the options for the user
  with the brainstorming **visual companion** (`superpowers:brainstorming`) and let
  them click, instead of asking in prose. "Which of these feels right?" is for the
  companion; "what should this do?" stays in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** (WCAG 2.2 AA, grouped by POUR) against the
   screen or component you're auditing.
2. Reach for a fix in **`references/snippets.md`** (labelled field, icon button,
   focus management, live region, RN roles, reduced motion).
3. Check **`references/pitfalls.md`** before you ship — most a11y bugs are on it.

## Related

- Building the component itself → `component-design`
- Accessible forms, labels, and error messaging → `forms-and-validation`
- Motion that respects reduced-motion → `animation-and-motion`
- Color tokens and contrast → `styling-systems`
- Testing behavior via roles and names → `frontend-testing`
- Touch-target size and gestures on mobile → `touch-interaction`
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
