---
name: data-fetching
description: Handle async data the house way — treat server state as a cache (not useState + useEffect), render loading/error/empty/success explicitly, fetch with keys/dedup/revalidation, and mutate optimistically then reconcile. Use when fetching data in a component, adding caching, wiring loading/error states, building a mutation, or reviewing data-fetching code.
---

# Data fetching

Stack-agnostic principles, concrete examples in React 19 and React Native.
The patterns port to Vue/Svelte and other query libraries; the judgments don't change.

**Version targets:** React 19, React Native 0.81 (current stable) / Expo SDK 54,
TanStack Query v5. Snippets grounded against Context7 (`/reactjs/react.dev`,
`/tanstack/query`, `/facebook/react-native`) at authoring time — see `references/snippets.md`.

## The core question

Every data-fetching decision reduces to: *is this server state or client state?*
Server state lives on a server, is fetched asynchronously, can be shared, and goes
stale — it's a **cache you borrow**, not state you own. Treat it as a cache (dedup,
revalidate, expire) and most loading/error/staleness bugs disappear. Genuine client
state (form input, which tab is open) is the only thing you truly own with `useState`.

## Principles

- **Server state is a cache, not `useState`.** The `useEffect`-fetch-into-`useState`
  pattern re-implements caching badly: no dedup, no revalidation, request races, stale
  closures, a refetch on every mount. Reach for a cache — TanStack Query / SWR, or
  React 19 `use()` + Suspense — that owns fetching, caching, and refetching.
- **Every async read has four states. Render all of them.** Loading, error, empty
  (resolved but zero rows), and success. A component that assumes `data` is present
  crashes on the first slow network or empty result. Make the states explicit — a
  discriminated result, or Suspense + an error boundary.
- **Key data by its inputs; serve stale-while-revalidate.** A query is identified by
  its key (`['user', id]`). Same key → shared, deduped, cached. Show cached data
  instantly and revalidate in the background; set `staleTime` so you don't refetch
  what's still fresh.
- **Prefer declarative boundaries to per-component `if (loading)` ladders.** React 19's
  `use()` reads a promise and suspends; a `<Suspense>` ancestor renders the fallback and
  an error boundary catches rejection. One place for loading, one for errors — not
  ternaries scattered through every component.
- **Mutations: update optimistically, then reconcile.** Show the result immediately
  (React 19 `useOptimistic` / a form `action`, or a cache write via `onMutate`), confirm
  against the server, and roll back on failure. Invalidate the affected queries so the
  cache re-syncs with the truth.
- **Co-locate fetching with the component that needs it — but keep it out of
  presentational components.** The data owner fetches; the presentational shell takes
  data as props (the `component-design` "separate layout from data" rule). Don't
  prop-drill server state through five layers — read it from the cache where it's used.
- **Mobile parity.** The same cache-not-state rules hold in React Native; the
  differences are platform wiring — refetch on app foreground (`AppState`) and on
  reconnect (NetInfo), there's no SSR, and every request needs a timeout/abort because
  mobile networks drop silently. See `references/pitfalls.md`.

## How to use this skill

1. Run **`references/checklist.md`** against the read or mutation you're writing or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (React 19 `use()` + Suspense,
   TanStack Query read, optimistic mutation, React Native wiring).
3. Check **`references/pitfalls.md`** before you ship — the `useEffect` fetch and the
   missing error state catch almost everyone.

## Related

- Where data lives once fetched / sharing it across components → `state-management`
- The component that renders it → `component-design`
- A form that submits it → `forms-and-validation`
- Testing fetch/mutation behavior → `frontend-testing`
- Waterfalls, over-fetching, slow lists → `frontend-performance`
