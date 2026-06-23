# Mobile navigation pitfalls

## Routing what is really state
**Symptom:** a route pushed to open a bottom sheet, dropdown, or "edit mode" — the
back button closes the sheet, deep links land oddly, history fills with non-destinations.
**Fix:** if it isn't shareable / deep-linkable / restorable, it's `useState`, not a
route. Reserve routes for destinations.

## Passing whole objects as params
**Symptom:** `navigate("Details", { item })` with a full object (or a function/date).
Deep links break, state restoration drops the screen, warnings about non-serializable params.
**Fix:** pass an id; the destination fetches its own data. React Navigation persists
and deep-links only JSON-serializable params.

## Untyped routes
**Symptom:** a typo'd route name or a forgotten param is a runtime blank screen, not
a compile error.
**Fix:** declare a `RootStackParamList` (or Expo typed routes / React Router types)
and register it so `useNavigation` and `route.params` are checked.

## Stacking instead of resetting
**Symptom:** after login the user can swipe back to the login screen; tab switches
pile onto the stack; back lands somewhere nonsensical.
**Fix:** choose `push` / `navigate` / `reset` deliberately. Auth transitions and tab
switches replace history; only true drill-down pushes.

## Ignoring the Android hardware back
**Symptom:** the hardware back button exits the app or does the wrong thing because
only the header back was wired.
**Fix:** let the navigator own back where it can; for custom flows handle it
explicitly (e.g. `BackHandler` / a route-level back behavior) and test on Android.

## Over-nesting navigators
**Symptom:** tabs inside a stack inside tabs to force a layout; transitions and back
behavior get strange.
**Fix:** the navigator tree should mirror the IA, not patch a layout problem. Flatten,
and move shared chrome into a layout or per-screen `options`.

## Deep linking bolted on last
**Symptom:** links work only when the app is already open; cold-start links land on
the wrong screen.
**Fix:** design the path↔param mapping with the structure and test cold (app killed).
If a screen can't be expressed as a URL, the structure is the problem.

## Heavy work in the navigator
**Symptom:** every tab and screen mounts and fetches at app start; first paint is slow.
**Fix:** let screens mount lazily (the default for React Navigation tabs and Expo
Router), fetch in the screen from its param, and keep transition work cheap →
`native-performance`.
