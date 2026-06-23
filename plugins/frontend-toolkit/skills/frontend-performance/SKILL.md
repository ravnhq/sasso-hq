---
name: frontend-performance
description: Diagnose and fix frontend performance — Core Web Vitals (LCP, INP, CLS), JavaScript bundle size, and React render cost — with a measure-first method. Use when a page loads or responds slowly, a bundle is too large, a list or view janks, Lighthouse / Web Vitals scores are poor, or before shipping a perf-sensitive feature.
---

# Frontend performance

Stack-agnostic method, concrete examples in React 19 and React Native. The tools
change per framework; the method — measure, fix the bottleneck, verify — does not.

**Version targets:** React 19, React Native 0.81 (current stable), web-vitals v4+
(INP-based; FID was retired). Snippets grounded against Context7
(`/reactjs/react.dev`, `/facebook/react-native`, `/googlechrome/web-vitals`) at
authoring time — see `references/snippets.md`.

## The core method

Performance work is a loop, not a bag of tricks: **measure → find the bottleneck →
fix it → re-measure.** Optimizing without a measurement is guessing, and guesses
usually add complexity without moving a number. Profile first — the slow thing is
rarely where you'd guess — then change one thing and confirm it helped.

The three places frontend time goes, each with its own metric and its own fix:

- **Loading** — how fast meaningful content paints. Watched by **LCP** (≤ 2.5s) and
  **CLS** (≤ 0.1). Usually a *bundle* and *critical-path* problem.
- **Responsiveness** — how fast the UI reacts to input. Watched by **INP** (≤ 200ms).
  Usually a *rendering* problem (too much work on the main thread per interaction).
- **Runtime smoothness** — scrolling, animation, list rendering. Watched with the
  Performance panel / React DevTools Profiler. A *rendering* and *virtualization* problem.

(Thresholds are the "good" bar at the 75th percentile of real users.)

## Principles

- **Measure before you optimize.** Use field data (the `web-vitals` library, CrUX)
  for what real users feel and lab tools (Lighthouse, the Performance panel, the
  React DevTools Profiler) to find *why*. No profile, no fix.
- **Fix the critical path first.** A user waits on LCP and INP, not on your
  cleverest micro-optimization. Spend effort on what's between request and first
  interaction before anything below the fold.
- **Ship less JavaScript.** The cheapest code is the code you never send.
  Code-split routes, lazy-load below-the-fold and heavy/rarely-used components,
  tree-shake, and audit a dependency's cost before adding it.
- **Render less, less often.** Most "React is slow" is too many re-renders or too
  much work per render. Memoize deliberately (or let the React Compiler do it),
  virtualize long lists, and split blocking updates from non-blocking ones
  (`useTransition` / `useDeferredValue`).
- **Reserve space to kill layout shift.** CLS comes from images, ads, embeds, and
  fonts that arrive without reserved dimensions. Set explicit `width`/`height`,
  use `font-display`, and never insert content above what the user is reading.
- **Verify, then guard.** Re-measure after every change — an "optimization" that
  doesn't move a metric is just added risk. Lock the win in with a budget
  (bundle-size check or Lighthouse CI) so it can't silently regress.
- **Mobile parity.** The same measure-first loop holds in React Native, but the
  levers differ (JS thread, list virtualization, bridge/serialization cost).
  Deep RN work belongs in `native-performance`; see `references/pitfalls.md`.

## How to use this skill

1. Run **`references/checklist.md`** against the page or interaction you're
   profiling or reviewing — it's ordered measure-first.
2. Reach for a pattern in **`references/snippets.md`** (measure Web Vitals,
   code-split, keep input responsive, skip re-renders, virtualize an RN list).
3. Check **`references/pitfalls.md`** before you ship — most perf PRs hit at least one.

## Related

- Deep React Native render/list/bridge cost → `native-performance`
- Caching, request waterfalls, loading/error states → `data-fetching`
- Re-renders caused by state architecture → `state-management`
- Animations that must stay at 60fps and respect reduced-motion → `animation-and-motion`
- Asserting behavior (not perf) in tests → `frontend-testing`
