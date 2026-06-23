# Mobile navigation checklist

Run this against any navigation you add or review.

## Structure
- [ ] Does the navigator tree mirror the app's information architecture (stacks for drill-down, tabs for peer sections, modals for interruptions)?
- [ ] Is nesting deliberate and shallow — no tab-inside-stack-inside-tab to paper over a layout problem?
- [ ] Is each screen a real destination (URL-addressable), not local UI state dressed up as a route?

## Routes vs state
- [ ] Is everything that should be deep-linkable / shareable / restorable a route — and everything that shouldn't be just local state?
- [ ] Is there one source of truth for "where am I" (the navigation state), not a parallel `useState` mirror?

## Params & typing
- [ ] Do params carry a minimal JSON-serializable identity (an `id`), not whole objects, functions, or dates?
- [ ] Is the route map typed (`RootStackParamList` / Expo typed routes / React Router types) so bad routes and missing params fail at compile time?
- [ ] Does the screen fetch its own data from the param, rather than expecting the pushing screen to hand it the object?

## Back & history
- [ ] Does every push have a sane back destination?
- [ ] Are `push` / `navigate` / `reset` chosen deliberately (auth and tab switches replace, not stack)?
- [ ] (RN) Is the Android hardware back handled where it should differ from the header back?

## Deep linking
- [ ] Does every screen map to a URL, with params expressed as path/query segments?
- [ ] Is `linking` (React Navigation) / the file route tree (Expo Router) configured, and tested cold — app fully killed, not just backgrounded?

## React Native specifics
- [ ] Are `react-native-screens` and `react-native-safe-area-context` installed, and the app wrapped correctly (`NavigationContainer` / Expo Router root)?
- [ ] Are headers, gestures, and the tab bar configured per-screen via `options`, not hand-rolled?
- [ ] Do heavy screens mount lazily rather than all at startup?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (gestures → `touch-interaction`, transition perf → `native-performance`, cross-screen state → `state-management`, a11y on route change → `accessibility-audit`.)
