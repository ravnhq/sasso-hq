---
name: touch-interaction
description: Build touch and gesture UX that feels native — thumb-sized targets, feedback on touch-down, and continuous gestures (drag, swipe, pinch) that track the finger on the UI thread without stealing scrolls. Use when adding a gesture, building a swipeable/draggable component, fixing janky or unresponsive touch, sizing tap targets, or reviewing touch interactions on web or React Native.
---

# Touch interaction

Stack-agnostic principles, concrete examples in React 19 (web) and React Native.
The native examples port to other gesture stacks; the judgments don't change.

**Version targets:** React 19 (web), React Native 0.81 / Expo SDK 54,
react-native-gesture-handler 2.x, react-native-reanimated 3.x/4.x (shared-value &
worklet API identical across both). Snippets grounded against Context7
(`/websites/swmansion_react-native-gesture-handler`,
`/websites/swmansion_react-native-reanimated`) at authoring time — see
`references/snippets.md`. The web snippet uses the W3C Pointer Events API + CSS
`touch-action` (platform standards).

## The core question

Every touch decision reduces to: *what is the finger doing, and does the surface
respond on the same frame?* A native feel comes from continuous gestures tracking
the finger 1:1 on the UI thread, discrete touches acknowledged within one frame,
and gestures that yield to the scroll unless the user clearly meant otherwise.
Latency and stolen scrolls read as "broken," not "slow."

## Principles

- **Continuous gestures belong on the UI thread.** A drag, pinch, or swipe that
  follows the finger must not round-trip through JS — under load the JS thread
  stalls and the gesture janks. Drive it from a worklet writing shared values
  (gesture-handler + Reanimated) on native, or Pointer Events with
  `setPointerCapture` on web. Hop to JS (`runOnJS`) only for the side effect.
- **Make targets thumb-sized.** Minimum 44×44pt (iOS HIG) / 48×48dp (Android
  Material). When the visual is smaller, *expand* the touch area — `hitSlop` and
  padding in React Native, padding or a `::before` overlay on web — don't shrink
  the target to the icon.
- **Feedback within one frame.** Acknowledge every touch on touch-*down*, not on
  release: pressed state, ripple, scale, or a haptic. A button that only reacts
  when the finger lifts feels dead.
- **Never steal a scroll.** A horizontal swipe inside a vertical list, a tap on a
  row — gestures must defer to the scroller unless intent is clear. Declare it with
  activation thresholds (`activeOffsetX`, `failOffsetY`) and `touch-action` on web,
  rather than greedily capturing the first touch.
- **Compose and disambiguate explicitly.** Single vs double tap, tap vs
  long-press, pan vs pinch — state how recognizers relate (`Race` / `Simultaneous`
  / `Exclusive`). The default of "they all fire" is rarely what you want.
- **A gesture is an enhancement, not the only path.** Custom swipes and
  long-presses need an accessible equivalent (a visible control, an a11y action)
  and must survive the screen reader, which intercepts raw touches. Honor
  reduced-motion for any gesture-driven animation. See `references/pitfalls.md`.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — target sizing or a gesture-affordance mockup — render the options for the
  user with the brainstorming **visual companion** (`superpowers:brainstorming`) and
  let them click, instead of asking in prose. "Which of these feels right?" is for
  the companion; "what should this do?" stays in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** against the interaction you're building or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (tap vs double-tap,
   UI-thread drag, swipe-to-action that respects the scroll, sized target with
   instant feedback, web pointer-drag).
3. Check **`references/pitfalls.md`** before you ship — most touch PRs hit at least one.

## Related

- Structuring screens, stacks, tabs, and the transitions between them → `mobile-navigation`
- The animation a gesture drives (springs, timing, shared transitions) → `animation-and-motion`
- Keeping gesture-driven lists and animations at 60fps → `native-performance`
- Screen-reader behavior and reduced-motion correctness → `accessibility-audit`
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
