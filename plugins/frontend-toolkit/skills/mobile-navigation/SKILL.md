---
name: mobile-navigation
description: Structure React Native (and React-family web) navigation correctly from the start — what's a route vs local state, typed params, stacks/tabs/modals, back behavior, and deep linking. Use when adding navigation to an app, adding a screen or flow, choosing React Navigation vs Expo Router, deciding what a route's params should carry, or reviewing navigation structure.
---

# Mobile navigation

Stack-agnostic principles, concrete examples in React Native (React Navigation,
Expo Router) and React-family web (React Router). The primitives differ; the
route-vs-state judgments don't.

**Version targets:** React 19, React Native 0.81, React Navigation 7, Expo SDK 54
(Expo Router), React Router 7 (web). Snippets grounded against Context7
(`/websites/reactnavigation`, `/websites/expo_dev`, `/remix-run/react-router`) at
authoring time — see `references/snippets.md`.

## The core question

Every navigation decision reduces to: *is this a destination or a state?* A
destination has a URL, survives reload and deep links, sits in history, and is
shareable — it's a route. A toggled panel, a selected segment, a sheet that
shouldn't be linkable — that's local state. Most broken navigation comes from
confusing the two: routing things that are really state, or hiding behind state
things that should be addressable.

## Principles

- **The navigator tree is your information architecture.** Stacks for push/pop
  drill-down, tabs for co-equal sections, modals/sheets for interruptions. Nest
  deliberately — a tab inside a stack inside a tab usually means the IA is wrong,
  not that you need more nesting.
- **Routes are addressable; UI state isn't.** If a place should be deep-linkable,
  shareable, restorable after reload, or reachable by the back button, it's a
  route. Otherwise it's `useState`. Don't push a route just to open a menu.
- **Params carry identity, not data.** Pass the smallest JSON-serializable key
  (an `id`), not whole objects; the screen fetches its own data from that key.
  This is what keeps deep links and state restoration working — React Navigation
  persists and deep-links only serializable params.
- **Type the route map from the start.** A typed param list (`RootStackParamList`,
  Expo typed routes, React Router types) turns a misspelled route or a missing
  param into a compile error instead of a runtime blank screen.
- **Design the back path, not just the forward one.** Every `navigate`/`push`
  needs a sane return. Choose `push` vs `navigate` vs `reset` deliberately —
  sign-in and tab switches should replace, not stack. On Android the hardware
  back button is part of your UI.
- **Deep linking is the test of your structure.** If every screen maps cleanly to
  a URL and its params, the structure is sound; if a screen can't be expressed as
  a URL, that's a design smell. It's the same path mapping on web (React Router)
  and native (React Navigation/Expo Router) — wire it early.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — tabs vs. stack, or the navigator tree as a diagram — render the options
  for the user with the brainstorming **visual companion**
  (`superpowers:brainstorming`) and let them click, instead of asking in prose.
  "Which of these feels right?" is for the companion; "what should this do?" stays
  in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** against the navigation you're adding or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (typed native stack, tabs
   under a stack, params, deep linking, Expo Router file-based, React Router web).
3. Check **`references/pitfalls.md`** before you ship — most navigation PRs hit at least one.

## Related

- Gestures and touch targets in navigation → `touch-interaction`
- Screen-transition cost, lazy screens, list-heavy screens → `native-performance`
- State that outlives a screen vs route/param state → `state-management`
- Focus and screen-reader announcements on route change → `accessibility-audit`
- Fetching a route's data from its params → `data-fetching`
- Designing the screen components themselves → `component-design`
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
