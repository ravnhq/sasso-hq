# Data fetching pitfalls

## `useEffect` + `useState` to fetch
**Symptom:** `useEffect(() => { fetch(url).then(setData) }, [])` — no caching, no dedup,
request races on fast input changes, stale closures, and a refetch on every mount.
**Fix:** use a server-state cache (TanStack Query / SWR) or React 19 `use()` + Suspense.
If you genuinely must use `useEffect`, add an `AbortController` and ignore stale responses
in the cleanup.

## Missing error / empty states
**Symptom:** the component renders `data.map(...)` and crashes (or shows a blank screen)
on a slow network, a rejected request, or a zero-row result.
**Fix:** render all four states — loading, error (with retry), empty, success. Don't let
`success` be the implicit default.

## Render-created promises with `use()`
**Symptom:** `use(fetchUser(id))` called inside the suspending component — a new promise
every render, so it suspends forever or refetches in a loop.
**Fix:** create the promise outside (cache it, or pass it as a prop from a stable parent);
`use` only *reads* it. For most apps, let a cache (Query) own the promise.

## Refetching data you already have
**Symptom:** the default `staleTime: 0` means every mount and refocus refetches fresh
data, flooding the network and flashing spinners.
**Fix:** set `staleTime` to how long the data is acceptably fresh. Serve cached data
instantly; revalidate in the background.

## Mutation without reconciliation
**Symptom:** a write succeeds but the UI still shows the old value because the cache was
never updated or invalidated.
**Fix:** on success, `invalidateQueries` for the affected keys (or patch the cache). For
instant feedback, update optimistically (`useOptimistic`, or `onMutate` + rollback) and
then reconcile.

## Waterfalls from sequential awaits
**Symptom:** components fetch in sequence (A renders → fetches → B renders → fetches), so
total latency is the sum, not the max.
**Fix:** start independent requests together (parallel queries, prefetch on the parent, or
hoist the promise). Sequential is only correct when B genuinely needs A's result. (Deeper
latency work → `frontend-performance`.)

## RN: no foreground / reconnect refetch
**Symptom:** a mobile app shows hours-old data after being backgrounded, or never recovers
after the network drops.
**Fix:** wire `focusManager` to `AppState` and `onlineManager` to NetInfo (see snippets),
and give every request a timeout / abort — mobile networks fail silently.
