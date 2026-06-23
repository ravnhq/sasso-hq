# Native performance checklist

Run this over a screen that janks, drops frames, or re-renders too much. **Measure
first** — confirm the bottleneck with a profiler before changing any code.

## Measure
- [ ] Reproduced the jank and captured it in a profiler? (React DevTools Profiler for re-renders; the Hermes sampling profiler for JS-thread time.)
- [ ] Identified *what* is expensive — render count, a slow function, or a native crossing — rather than guessed?
- [ ] Have a before-number to compare the fix against?

## List virtualization
- [ ] Is a long list rendered with a virtualized list (`FlatList`/`SectionList`/`FlashList`), not `.map()` inside a `ScrollView`?
- [ ] Is `keyExtractor` stable and unique (not the array index)?
- [ ] For fixed-height rows, is `getItemLayout` provided (including separator height) so the list skips measurement?
- [ ] Does a row read anything outside `data` (selection, theme)? If so, is it passed via `extraData`?
- [ ] Tuning considered for the data size — `initialNumToRender`, `maxToRenderPerBatch`, `windowSize`? (`removeClippedSubviews` only with care — it can drop visible content.)

## Render cost
- [ ] Is the expensive subtree memoized (`React.memo`) with `===`-stable props — or are you on the React Compiler (then drop the manual memo)?
- [ ] Are callbacks/objects/styles passed to memoized children hoisted (`useCallback`/`useMemo`/`StyleSheet.create`), not allocated inline per render?
- [ ] Is each value derived from one source of truth, not copied into a second `useState`?
- [ ] Is state lifted no higher than its lowest common owner? (Lifting widens the re-render scope.)

## Native / bridge cost (React Native)
- [ ] Are scroll/gesture-linked values driven on the native thread (`useNativeDriver`, Reanimated), not via per-frame `setState`?
- [ ] Is the New Architecture enabled (Fabric + TurboModules) and Hermes the JS engine?
- [ ] Is heavy synchronous work kept off the interaction path (`InteractionManager.runAfterInteractions`, chunking, or `useDeferredValue`/`useTransition`)?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (web rendering/bundle perf → `frontend-performance`, animations → `animation-and-motion`, component/row shape → `component-design`, over-fetching → `data-fetching`.)
