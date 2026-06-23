# Frontend performance pitfalls

## Optimizing without measuring
**Symptom:** memoizing, splitting, and rewriting based on a hunch about what's slow.
**Fix:** profile first (Lighthouse, Performance panel, React DevTools Profiler, field
`web-vitals`). Find the actual bottleneck, change one thing, re-measure. No number, no fix.

## Measuring the dev build
**Symptom:** "it's so slow" — measured against an unminified dev build with extra
warnings, Strict Mode double-renders, and no production optimizations.
**Fix:** profile a production build. Treat dev timings as directional only.

## Blanket memoization
**Symptom:** `memo`/`useMemo`/`useCallback` on everything "to be safe" — code is noisy
and sometimes *slower* (memo and dependency comparison aren't free).
**Fix:** memoize where a profile shows a re-render cost, not reflexively. With the React
Compiler on, delete the manual memoization and let it do this automatically.

## Unstable props defeating memo
**Symptom:** a `memo`'d child still re-renders every time because it gets a fresh inline
`{}`/`() => {}` prop, or a context value rebuilt each provider render.
**Fix:** hoist callbacks with `useCallback`, objects with `useMemo`; memoize the context
`value`. memo only helps when props are `===`-stable.

## Bloated bundle from barrel/whole-library imports
**Symptom:** `import { thing } from "huge-lib"` (or a barrel `index`) pulls the whole
library; the initial chunk is megabytes.
**Fix:** look at a bundle analysis, import the specific module, prefer tree-shakeable
named imports, code-split routes/heavy components with `lazy`, and add a size budget in CI.

## Layout shift from unsized or late content
**Symptom:** content jumps as images, ads, embeds, or fonts load; CLS is poor.
**Fix:** reserve space — explicit `width`/`height` or aspect-ratio on media — use
`font-display` with a size-adjusted fallback, and never inject content above what's
already on screen.

## Request waterfalls blocking first paint
**Symptom:** components fetch in sequence (each `useEffect` waits for the parent's data),
so the screen fills in slowly one box at a time.
**Fix:** fetch in parallel, hoist/prefetch, and colocate loading with a caching layer.
This is `data-fetching`'s domain — reach for it.

## RN: an unvirtualized list
**Symptom:** a long list built with `.map()` inside a `ScrollView` mounts every row up
front; the screen is slow to open and janks on scroll.
**Fix:** use `FlatList`/`FlashList` (virtualized), add `getItemLayout` for fixed-height
rows, and memoize the row. Deeper RN render/bridge cost → `native-performance`.
