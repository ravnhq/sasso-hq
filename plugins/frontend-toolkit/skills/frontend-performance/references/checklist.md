# Frontend performance checklist

Run this against a slow page or interaction. It's ordered **measure-first** — don't
skip to the fixes.

## Measure first
- [ ] Do you have a number to beat? (LCP/INP/CLS from field data, or a Lighthouse / Profiler trace.)
- [ ] Is the bottleneck identified from a profile, not a hunch? (The slow thing is rarely the obvious one.)
- [ ] Are you measuring a production-like build? (Dev builds are slow and misleading — no minification, extra warnings.)
- [ ] Will you re-measure the *same way* after the fix to prove the win?

## Loading & LCP (≤ 2.5s)
- [ ] Is the LCP element (usually the hero image or heading) discoverable early — not hidden behind JS or lazy-loaded?
- [ ] Are render-blocking resources minimized (critical CSS inlined, non-critical JS deferred/`async`)?
- [ ] Are images sized, modern-format, and `priority`/eager only for the LCP one (the rest `loading="lazy"`)?
- [ ] Are fonts preloaded with `font-display: swap` so text isn't invisible while they load?

## Layout stability (CLS ≤ 0.1)
- [ ] Do images, video, embeds, and ad slots reserve space (explicit `width`/`height` or aspect-ratio)?
- [ ] Is content never inserted above existing content after load (banners, late-loading widgets)?
- [ ] Do web fonts avoid a layout-shifting swap (size-adjusted fallback)?

## Responsiveness (INP ≤ 200ms)
- [ ] Is per-interaction main-thread work small, or broken up (no long tasks > 50ms blocking input)?
- [ ] Are expensive, non-urgent updates deferred (`useTransition` / `useDeferredValue`) so typing/clicks stay snappy?
- [ ] Are large lists virtualized rather than rendering every row on each keystroke?

## Bundle
- [ ] Have you looked at a bundle analysis (what's actually big)?
- [ ] Are routes and heavy/rarely-used components code-split (`lazy` + `Suspense`)?
- [ ] Are imports tree-shakeable (named imports, no whole-library/barrel imports pulling everything)?
- [ ] Is each heavy dependency justified, or is there a lighter alternative / native API?
- [ ] Is there a bundle-size budget in CI so this doesn't regress?

## Rendering (React)
- [ ] Have you confirmed *which* components re-render and *why* (Profiler / "why did you render")?
- [ ] Are expensive children `memo`-wrapped with stable (`useCallback`/`useMemo`) props — or is the React Compiler doing it?
- [ ] Are you memoizing because a profile showed a cost, not reflexively? (memo has its own cost.)
- [ ] Are context values memoized so every consumer doesn't re-render on each provider render?

## React Native parity (if applicable)
- [ ] Long lists use `FlatList`/`FlashList` (virtualized), never `.map()` inside a `ScrollView`?
- [ ] Fixed-height rows provide `getItemLayout` to skip measurement?
- [ ] Row components are `memo`'d with stable callbacks, and `extraData` covers anything read outside `data`?
- [ ] (Deeper RN render/bridge work → hand off to `native-performance`.)

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (RN deep-dive → `native-performance`, fetch/caching → `data-fetching`, state-driven re-renders → `state-management`, motion → `animation-and-motion`.)
