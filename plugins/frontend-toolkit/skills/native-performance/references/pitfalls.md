# Native performance pitfalls

## `.map()` into a `ScrollView`
**Symptom:** a long list built with `data.map(...)` inside a `ScrollView`; scroll
is janky and memory grows with the data.
**Fix:** use a virtualized list (`FlatList`/`SectionList`/`FlashList`). A
`ScrollView` mounts every child; virtualization mounts only the visible window.

## Inline allocation in the render path
**Symptom:** a memoized row still re-renders every frame because it receives a new
arrow function, object, or inline `style={{...}}` on each parent render.
**Fix:** hoist callbacks with `useCallback`, objects with `useMemo`, and styles to
`StyleSheet.create`/module scope. `memo` only helps when props are `===`-stable.

## Forgetting `extraData`
**Symptom:** tapping a row doesn't update its selected style until you scroll it
out of view and back.
**Fix:** `FlatList` is a `PureComponent`; when a row reads state outside `data`
(selection, theme), pass it via `extraData` so the list knows to re-render.

## Array index as key
**Symptom:** the wrong rows recycle or animate, and state attaches to the wrong
item after an insert or reorder.
**Fix:** give `keyExtractor` a stable, unique id — not the array index.

## `getItemLayout` on variable-height rows
**Symptom:** scroll-to-index lands in the wrong place; blank gaps appear while
scrolling.
**Fix:** only use `getItemLayout` for genuinely fixed-height rows, and include
separator height in the offset. For variable heights, omit it (or measure).

## Per-frame `setState` from scroll or gesture
**Symptom:** a parallax or sticky header driven by `onScroll → setState` drops
frames.
**Fix:** keep the value in an `Animated.Value` with `useNativeDriver: true` (or
Reanimated) so it animates on the native thread without re-rendering React.

## Over-memoization
**Symptom:** `memo`/`useMemo`/`useCallback` sprinkled over everything, including
cheap components; the code is harder to read and no faster.
**Fix:** measure first and memoize the proven hot spot only. Better, adopt the
React Compiler (React 19) and delete the manual memoization entirely.

## Optimizing without measuring
**Symptom:** changes made on a hunch; the jank persists because the real cost was
elsewhere.
**Fix:** profile first — React DevTools Profiler for re-renders, the Hermes
sampling profiler for JS time. Optimize the measured bottleneck, then re-measure.

## Heavy work blocking the JS thread
**Symptom:** typing or navigation freezes while a large synchronous computation
runs.
**Fix:** defer it — `useDeferredValue`/`useTransition` (web + RN), or
`InteractionManager.runAfterInteractions`/chunking on native — so input stays live.
