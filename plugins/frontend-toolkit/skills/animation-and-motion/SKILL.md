---
name: animation-and-motion
description: Add motion that communicates and stays cheap — animate compositor-only properties (transform/opacity), drive it off the main/JS thread, and honor reduced-motion preferences on web and React Native. Use when adding a transition or animation, building a motion-heavy interaction, fixing janky or expensive animation, or making motion respect prefers-reduced-motion / OS accessibility settings.
---

# Animation and motion

Stack-agnostic principles, concrete examples in React 19 and React Native.
The examples port to Vue/Svelte and to Motion/Reanimated; the judgments don't change.

**Version targets:** React 19, React Native 0.81 (current stable), with library
notes for Motion (`motion/react`) and Reanimated 4. Snippets grounded against
Context7 (`/reactjs/react.dev`, `/facebook/react-native`, swmansion Reanimated,
`motion.dev`) at authoring time — see `references/snippets.md`.

## The core question

Every motion decision reduces to: *what does this animation tell the user?* Good
motion communicates — it orients (where did this come from), gives feedback (your
tap registered), or shows continuity (this list reordered, it didn't teleport).
Motion that conveys nothing is cost without benefit, and on a slow device or for a
motion-sensitive user it's actively harmful. If you can't name what an animation
communicates, it's a candidate for deletion.

## Principles

- **Animate compositor-only properties.** `transform` and `opacity` are handled by
  the compositor and don't trigger layout or paint. Animating `width`, `height`,
  `top`, `margin`, or `box-shadow` reflows the page every frame and drops frames.
  On React Native the same split exists: `useNativeDriver: true` runs the animation
  on the UI thread but only supports `transform`/`opacity`.
- **Respect reduced motion — it's not optional.** Honor `prefers-reduced-motion`
  (web) and `AccessibilityInfo.isReduceMotionEnabled()` (RN). And *reduce*, don't
  blindly remove: swap a large slide or scale for a quick cross-fade, keep the
  essential state feedback. Ignoring this can trigger vestibular symptoms and fails
  WCAG 2.3.3.
- **Keep it short and interruptible.** UI feedback lives in ~150–300ms. Longer,
  un-cancelable animations make the UI feel sluggish and queue up. New user input
  should be able to interrupt motion already in flight.
- **Don't animate React state per frame.** Driving an animation with `setState` in a
  `requestAnimationFrame`/`setInterval` loop re-renders every frame and churns the
  GC. Let the platform animate outside React's render: CSS, the Web Animations API,
  `Animated`, or Reanimated worklets.
- **Animate the cheap proxy, not the layout.** For enter/exit and reordering, use a
  transform-based approach (e.g. FLIP — measure first/last, animate the delta with
  `transform`) instead of animating layout properties directly.
- **Mobile parity.** The same meaning-and-cost rules hold in React Native; the
  difference is the native driver and that motion inside list rows multiplies across
  every visible row. Drive it on the UI thread and keep per-row work tiny. See
  `references/pitfalls.md`.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — which motion treatment or easing, shown as side-by-side demos — render
  the options for the user with the brainstorming **visual companion**
  (`superpowers:brainstorming`) and let them click, instead of asking in prose.
  "Which of these feels right?" is for the companion; "what should this do?" stays
  in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** against the motion you're adding or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (reduced-motion hooks,
   compositor-only CSS, the Motion config, RN native-driver `Animated`, Reanimated).
3. Check **`references/pitfalls.md`** before you ship — most motion PRs hit at least one.

## Related

- State that drives the animation → `state-management`
- Durations, easings, and motion tokens as design system → `styling-systems`
- Reduced motion as part of a full audit → `accessibility-audit`
- Dropped frames, bundle cost, render thrash → `frontend-performance` (web) / `native-performance` (RN)
- Gesture- and drag-driven motion on mobile → `touch-interaction`
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
