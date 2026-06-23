# Data fetching checklist

Run this against any data read or mutation you write or review.

## Server vs client state
- [ ] Is this server state (fetched, shareable, goes stale)? If so, is it in a cache (Query/SWR or `use()` + Suspense) — *not* `useState` + `useEffect`?
- [ ] Is the only thing in `useState` genuinely client-owned (form input, open/closed, selection)?

## The four states
- [ ] Is loading rendered (skeleton / spinner / Suspense fallback)?
- [ ] Is error rendered with a retry path — not a blank screen or a crash?
- [ ] Is empty (`data` resolved but zero rows) handled distinctly from loading?
- [ ] Does success never assume `data` is non-null before it has resolved?

## Caching & keys
- [ ] Does the query have a stable key derived from its inputs (`['user', id]`)?
- [ ] Is `staleTime` set deliberately, so you aren't refetching still-fresh data on every mount/refocus?
- [ ] Are concurrent reads of the same key deduped (one request, shared result)?
- [ ] Are requests aborted (`signal`) when inputs change or the component unmounts?

## Mutations
- [ ] Optimistic update where it improves UX, with rollback on error?
- [ ] Affected queries invalidated (or the cache patched) on success, so reads re-sync?
- [ ] Is the trigger disabled / a pending state shown while the mutation is in flight?

## React Native parity (if applicable)
- [ ] Refetch on app foreground (`AppState`) and on reconnect (NetInfo) wired?
- [ ] Does every request have a timeout / `AbortController` (mobile networks drop)?
- [ ] No reliance on SSR or web window-focus events?

## Reuse / boundaries
- [ ] Is fetching kept out of presentational components (data owner fetches; shell takes props)?
- [ ] Does a sibling skill own part of this? (cross-component cache → `state-management`; the form → `forms-and-validation`; waterfalls / over-fetch → `frontend-performance`.)
