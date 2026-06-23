---
name: native-performance
description: Keep React Native (and React-family) apps smooth — list virtualization, native-bridge cost, and render cost. Use when a list janks or drops frames, when scrolling or gestures stutter, when a screen re-renders too much, or when profiling a slow mobile UI.
---

# Native performance

Stack-agnostic principles, concrete examples in React Native and React 19. The
three costs below — *rendering too much*, *crossing the native boundary too
often*, and *mounting rows you can't see* — have web analogs; the judgments port,
the mechanisms differ.

**Version targets:** React 19 (with the React Compiler), React Native 0.81 on the
New Architecture (Fabric + JSI + TurboModules, bridgeless — default since RN 0.76).
Snippets grounded against Context7 (`/reactjs/react.dev`, `/facebook/react-native`)
at authoring time — see `references/snippets.md`.

## The core question

Performance work reduces to one question asked in the right place: *what is this
screen paying for, and is it paying per frame?* A cost paid once is fine; the same
cost paid on every render, every row, or every scroll event is where apps jank.
Find where you pay per frame — then stop paying.

## Principles

- **Measure before you optimize.** Profile the actual jank (React DevTools
  Profiler for re-renders, the Hermes sampling profiler for JS-thread time) before
  changing code. Memoizing the wrong component adds clutter and zero speed.
  Guessing is the bug.
- **Virtualize long lists.** Never `.map()` hundreds of rows into a `ScrollView` —
  that mounts every row. Use a virtualized list (`FlatList`/`SectionList`, or
  Shopify's recycling `FlashList`) so only the visible window is mounted.
- **Make rows cheap and `===`-stable.** A virtualized list is a `PureComponent`:
  it skips a row only when that row's props are shallow-equal. Memoize the item,
  hoist its callbacks, and pass `extraData` for anything the row reads outside `data`.
- **Don't cross the native boundary per frame.** Driving an animation or
  scroll-linked value through JS `setState` round-trips the React tree every
  frame. Keep it on the native/UI thread (`useNativeDriver`, Reanimated). The New
  Architecture (JSI) makes individual native calls cheap, but fewer crossings still win.
- **Render less, not just faster.** The cheapest render is the one that doesn't
  happen. Lift nothing extra, derive instead of copying state, and let memoized
  boundaries stop re-renders from propagating. On React 19 the React Compiler
  applies this memoization for you — adopt it and delete the manual `useMemo`/
  `useCallback`/`memo` noise.
- **Keep the JS thread free for interaction.** Heavy synchronous work blocks
  gestures and scrolling. Defer it (`useTransition`/`useDeferredValue` on web,
  `InteractionManager` or chunking on native) so input stays responsive.

## How to use this skill

1. Reproduce and **measure** the jank first — see the profiling note at the top of
   `references/checklist.md`. Optimize against numbers, not hunches.
2. Run **`references/checklist.md`** over the slow screen (list, render, bridge).
3. Reach for a pattern in **`references/snippets.md`** (virtualized list, memoized
   row, native-driven scroll value, deferred work).
4. Check **`references/pitfalls.md`** — most perf PRs are caused by one of them.

## Related

- Web rendering, bundle size, and code-splitting → `frontend-performance`
- Cheap, well-bounded components and list items → `component-design`
- Animations that run off the JS thread → `animation-and-motion`
- Fetching less and caching it → `data-fetching`
