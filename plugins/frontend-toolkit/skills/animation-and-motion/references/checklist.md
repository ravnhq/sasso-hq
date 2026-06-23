# Animation and motion checklist

Run this against any animation or transition you add or review.

## Purpose
- [ ] Can you name what this motion communicates (orientation, feedback, continuity)? If not, cut it.
- [ ] Would the UI be measurably worse without it, or is it decoration?
- [ ] Is it doing the *least* motion that still communicates the change?

## Performance
- [ ] Are you animating only `transform` and `opacity` (compositor-only), not `width`/`height`/`top`/`margin`/`box-shadow`?
- [ ] On React Native, is `useNativeDriver: true` set (and used only for `transform`/`opacity`)?
- [ ] Is the animation driven by the platform (CSS / WAAPI / `Animated` / Reanimated), not per-frame `setState`?
- [ ] Is `will-change` (web) applied sparingly and removed after, not left on many elements?

## Reduced motion
- [ ] Is `prefers-reduced-motion` honored on web (media query and/or a `useReducedMotion` hook)?
- [ ] Is `AccessibilityInfo.isReduceMotionEnabled()` honored on React Native (and updated on `reduceMotionChanged`)?
- [ ] Under reduced motion, do you *reduce* (cross-fade, instant) rather than strip essential feedback entirely?
- [ ] Did you actually test with the OS reduced-motion toggle on?

## Timing & interruption
- [ ] Is the duration in a sane range for its job (~150–300ms for UI feedback)?
- [ ] Can new user input interrupt or cancel motion that's in flight?
- [ ] Do animations avoid blocking input or queuing up behind each other?

## Mobile parity (if applicable)
- [ ] Is motion driven on the UI thread (native driver or Reanimated worklets), never per-frame on the JS thread?
- [ ] Is motion inside list rows cheap and bounded — it runs once per visible row?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (motion tokens → `styling-systems`, a11y audit → `accessibility-audit`, frame cost → `frontend-performance` / `native-performance`, gestures → `touch-interaction`.)
