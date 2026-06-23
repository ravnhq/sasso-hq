# Touch interaction pitfalls

## Gesture handled on the JS thread
**Symptom:** a drag/swipe that follows the finger via `setState` (or an
`Animated.Value` with `useNativeDriver: false`) stutters whenever the JS thread is
busy — list rendering, network parsing.
**Fix:** run the gesture in a worklet writing Reanimated shared values, read them in
`useAnimatedStyle` — both on the UI thread. Hop to JS (`runOnJS`) only for the side
effect at the end. (Smoothness of the surrounding list is `native-performance`.)

## The gesture fights the scroll (or vice versa)
**Symptom:** a swipeable row eats vertical scrolls, or the list scrolls when the
user meant to swipe.
**Fix:** set activation thresholds — `activeOffsetX([-10, 10])` to claim only after
horizontal travel, `failOffsetY([-8, 8])` to yield on vertical travel. On web, set
`touch-action: pan-y` so the browser keeps owning vertical scroll.

## Tiny touch targets
**Symptom:** a 16–24px icon is the tap target; users miss it, especially one-handed.
**Fix:** size the target to ≥44×44pt / 48×48dp with padding or `minWidth`/
`minHeight`, and add `hitSlop` (RN) or a padded hit area (web). Keep the *visual*
small if you like — grow the *target*.

## The ~300ms tap delay on web
**Symptom:** taps feel laggy in a mobile browser; a double-tap zooms the page.
**Fix:** set `touch-action: manipulation` on the interactive element (and a proper
`<meta name="viewport">`). Don't reach for a `fastclick`-style library — it's
obsolete.

## `setState`/navigation called straight from a worklet
**Symptom:** calling a plain JS function inside `onEnd`/`onUpdate` crashes or
silently does nothing once Reanimated workletizes the callback.
**Fix:** wrap it: `runOnJS(setOpen)(true)`. Keep shared-value math on the UI thread;
cross to JS only for React state, navigation, or analytics.

## Single-tap fires before the double-tap
**Symptom:** double-tap never triggers because the single-tap already fired on the
first touch; or both fire.
**Fix:** compose with `Gesture.Exclusive(doubleTap, singleTap)` so the double-tap
wins, or set `numberOfTaps(2)` with a sensible `maxDelay`. Don't run two independent
tap recognizers and hope.

## Interrupted gesture leaves the UI stuck
**Symptom:** an incoming call / notification / app-switch mid-drag leaves the element
half-moved or stuck in its pressed state.
**Fix:** reset in `onFinalize` (it always runs; check `event.canceled`) on native and
in `pointercancel` on web. Don't put cleanup only in `onEnd`/`pointerup` — those
don't fire when the OS cancels.

## Missing `GestureHandlerRootView`
**Symptom:** every gesture silently does nothing; no error.
**Fix:** wrap the app root in `<GestureHandlerRootView style={{ flex: 1 }}>`. Expo
Router and the RN template include it, but bare setups and isolated test trees often
don't.

## Custom gesture invisible to the screen reader
**Symptom:** a swipe-to-delete or long-press menu is unreachable with VoiceOver/
TalkBack on, which intercept raw touches.
**Fix:** provide a non-gesture path — a visible button and/or `accessibilityActions`
with `onAccessibilityAction`. The gesture is an enhancement, not the only door.
(Audit this with `accessibility-audit`.)
