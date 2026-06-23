# Touch interaction checklist

Run this against any touch surface or gesture you create or review.

## Touch targets
- [ ] Is every interactive target ≥ 44×44pt (iOS) / 48×48dp (Android)?
- [ ] When the visual is smaller, is the touch area expanded (`hitSlop`/padding on RN, padding/`::before` on web) rather than the target shrunk to the icon?
- [ ] Is there enough spacing between adjacent targets to avoid mis-taps?

## Feedback
- [ ] Does each touch get feedback on touch-*down* (pressed/active/ripple/scale), not only on release?
- [ ] Are haptics used for confirming/destructive actions — and not sprayed on every tap?
- [ ] Are disabled and loading states visually distinct and non-interactive?

## Gesture behavior
- [ ] Do continuous gestures run on the UI thread (gesture-handler + Reanimated worklets / pointer capture), not via JS-thread `setState` per move?
- [ ] Are competing recognizers composed deliberately (`Race`/`Simultaneous`/`Exclusive`); is single vs double vs long-press disambiguated?
- [ ] Is cancellation handled (`onFinalize`/`canceled`, `pointercancel`) so the UI resets cleanly when the OS interrupts (call, notification, app switch)?
- [ ] Does any `setState`/navigation called from a worklet go through `runOnJS`?

## Scroll & web specifics
- [ ] Does a gesture inside a scroller set activation thresholds (`activeOffsetX`/`failOffsetY`) so it doesn't fight the scroll?
- [ ] Is `touch-action` set on web to declare intent and kill the ~300ms tap delay (`manipulation`, `pan-y`)?
- [ ] Does a web drag use `setPointerCapture` so it keeps tracking when the finger leaves the element?
- [ ] Are scroll-path listeners passive; do only the gesture-owning ones call `preventDefault`?

## Accessibility & motion
- [ ] Does every custom gesture have a non-gesture equivalent (visible control + a11y action)?
- [ ] Is reduced-motion respected for gesture-driven animation?
- [ ] Does it still work with the screen reader on (VoiceOver/TalkBack intercept raw touches)?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (the animation → `animation-and-motion`; list/render smoothness → `native-performance`; a11y → `accessibility-audit`; screen transitions → `mobile-navigation`.)
