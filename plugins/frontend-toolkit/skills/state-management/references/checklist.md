# State management checklist

Run this against any state you add or review.

## Classify first
- [ ] Have you named the kind of state — local, server-cache, global-client, URL, or derived — *before* picking a tool?
- [ ] Who owns the source of truth (this component, the server, the whole app, the URL)?
- [ ] Is it derived? If it's computable from existing state/props, compute it during render — don't store it.

## Local state
- [ ] Is the state at the lowest common owner — not lifted "just in case"?
- [ ] Is `useReducer` warranted (several values that change together, or next-state depends on previous), or is `useState` simpler?
- [ ] Is there exactly one source of truth? (No `useEffect` copying props/state into more state.)

## Server-cache state
- [ ] Is server data in a query library (TanStack Query / RTK Query / SWR), not hand-managed in a global store or `useEffect` + `useState`?
- [ ] Is there a stable, serializable `queryKey` that identifies this data?
- [ ] After a mutation, do you `invalidateQueries` (or `setQueryData`) instead of mutating a separate copy?
- [ ] Are loading/error read from the query's status, not tracked by hand?

## Global client state
- [ ] Is it *genuinely* app-wide (theme, auth, feature flags, cross-route UI) — not just lifted too high?
- [ ] Does each consumer subscribe to the narrowest slice (a selector), so unrelated updates don't re-render it?
- [ ] For multi-value selects, are you using `useShallow` (or equivalent) to avoid a new-object-every-render re-render?
- [ ] Is the store small? Anything that's really server data or local state does not belong here.

## URL state
- [ ] Should this survive a reload or be shareable/bookmarkable (filters, tab, page, selected id)? If so, does the URL own it?
- [ ] Is the URL read as the source of truth, not mirrored into component state that can drift?

## React Native parity (if applicable)
- [ ] Is shareable/restorable state in navigation route params + deep links (the URL equivalent), not trapped in component state?
- [ ] Does server-cache refetch hook into navigation focus / app foreground (`focusManager` + `AppState`), not assume web window-focus?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (fetching mechanics → `data-fetching`, form field state → `forms-and-validation`, a single component's props → `component-design`.)
