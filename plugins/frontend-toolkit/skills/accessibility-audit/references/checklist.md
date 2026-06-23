# Accessibility audit checklist (WCAG 2.2 AA)

Run this against any screen, flow, or component. Grouped by the four WCAG
principles (POUR); target level is AA. Numbers in parentheses are WCAG 2.2
success criteria.

## Perceivable
- [ ] Every informative image has a text alternative; decorative images use empty `alt=""` / are hidden from AT (1.1.1).
- [ ] Color is never the only way information is conveyed (1.4.1).
- [ ] Text contrast ≥ 4.5:1 (≥ 3:1 for large text) (1.4.3); UI controls and meaningful graphics ≥ 3:1 (1.4.11).
- [ ] Layout survives 200% zoom and a 320px-wide viewport with no loss of content or function (1.4.4, 1.4.10).
- [ ] Structure uses real headings, lists, and landmarks — not styled `div`s (1.3.1).
- [ ] DOM/reading order and focus order match the visual order (1.3.2).
- [ ] Instructions don't depend on shape, size, or position alone ("the button on the right") (1.3.3).

## Operable
- [ ] Every interactive element is reachable and usable by keyboard alone (2.1.1).
- [ ] Focus is never trapped except inside an intentional modal (2.1.2).
- [ ] A visible focus indicator is present and not hidden behind sticky headers/footers (2.4.7, 2.4.11).
- [ ] A "skip to content" link or equivalent landmark navigation exists (2.4.1).
- [ ] Pages/screens have unique, descriptive titles and headings (2.4.2, 2.4.6).
- [ ] Link and button text makes sense out of context (no bare "click here") (2.4.4).
- [ ] Multi-point/path gestures have a single-pointer alternative; dragging has a non-drag path (2.5.1, 2.5.7).
- [ ] Touch/click targets are ≥ 24×24 CSS px (2.5.8) — 44pt iOS / 48dp Android in practice.
- [ ] Nothing flashes more than 3 times per second (2.3.1).
- [ ] Motion from interactions respects the user's reduced-motion preference (WCAG 2.3.3 is AAA — treat as a house baseline).

## Understandable
- [ ] Page/screen language is set (`<html lang>` / device locale) (3.1.1).
- [ ] Receiving focus or changing a field never triggers an unexpected context change (3.2.1, 3.2.2).
- [ ] Navigation and component identity stay consistent across screens (3.2.3, 3.2.4).
- [ ] Form fields have persistent, programmatically-associated labels — not placeholder-only (3.3.2).
- [ ] Errors are identified in text, tied to their field, and suggest a fix (3.3.1, 3.3.3).
- [ ] Help is reachable consistently; previously-entered data isn't demanded again (3.2.6, 3.3.7).
- [ ] Authentication doesn't rely on a memory/cognitive test (paste and password managers work) (3.3.8).

## Robust
- [ ] Custom controls expose a correct role, accessible name, and state to AT (4.1.2).
- [ ] Status messages reach AT without moving focus (live regions / announce) (4.1.3).
- [ ] ARIA is valid and minimal — every `aria-*` has a real effect and none contradicts native semantics.
- [ ] React Native: interactive nodes set `accessibilityRole`, `accessibilityLabel`, and `accessibilityState`; grouped content uses `accessible`.

## Verify with real tools (automation catches ~30–40%)
- [ ] Tab through the entire flow with no mouse — order sane, nothing unreachable, focus always visible.
- [ ] Drive the key path with a screen reader (VoiceOver / TalkBack / NVDA).
- [ ] Run an automated pass (axe / Lighthouse) and fix what it flags.

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (component shape → `component-design`, form labels/errors → `forms-and-validation`, motion → `animation-and-motion`, contrast tokens → `styling-systems`, behavior tests → `frontend-testing`, touch targets → `touch-interaction`.)
