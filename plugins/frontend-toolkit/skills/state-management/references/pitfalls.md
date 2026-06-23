# State management pitfalls

## Server data in a global store
**Symptom:** a Redux/Zustand slice holds API responses, with hand-written
`loading`, `error`, and `lastFetched` flags you update in `useEffect`.
**Fix:** that's server cache, not client state. Move it to a query library
(TanStack Query / RTK Query / SWR) — you get keys, status, refetch, and
invalidation for free. The store keeps only genuinely client-owned state.

## Everything is global
**Symptom:** a single screen's toggle, or a value only two sibling components
share, lives in the app-wide store "so it's easy to reach."
**Fix:** classify first. Most state is local — colocate it, and lift only to the
lowest common owner. Global state is a cost paid by every consumer.

## Duplicated source of truth (stored derived state)
**Symptom:** a `useEffect` copies props or state into a second `useState` — a
`fullName`, a `filteredList`, an `isValid` — that then drifts out of sync.
**Fix:** derive during render; there's one source of truth. If it's computable,
compute it (wrap in `useMemo` only when profiling says so).

## Over-broad store subscription
**Symptom:** `const state = useStore()` with no selector, or a selector returning a
fresh object/array each call — so the component re-renders on every store change.
**Fix:** select the narrowest slice (`useStore((s) => s.theme)`). For several
values at once, wrap the selector in `useShallow` so a new object doesn't force a
re-render every time.

## State that should live in the URL
**Symptom:** the active tab, filters, or page number sit in component state; a
reload or a shared link loses the user's place.
**Fix:** if it should survive reload or be shareable/bookmarkable, the URL owns it.
Read the URL as the source of truth; on native, that's navigation route params.

## Context for high-frequency state
**Symptom:** a fast-changing value (mouse position, a form draft, a timer) in
Context, re-rendering every consumer on every change.
**Fix:** Context has no selectors — any value change re-renders all consumers. Use
a selector store for frequently-updating global state, or colocate it if it isn't
really global.

## RN: server cache refetches on the wrong signal
**Symptom:** native screens show stale data after the app was backgrounded, or you
assume web window-focus refetching just works on React Native.
**Fix:** there's no window. Bridge `AppState` into `focusManager.setFocused` so the
cache refetches on foreground, and use a navigation focus effect for per-screen
refresh. See `references/snippets.md`.
