---
name: state-management
description: Choose where state belongs — local, server-cache, global-client, or URL — instead of reaching for one tool (Redux, Context, a global store) reflexively. Use when adding state to a feature, deciding whether something belongs in a global store, wiring up server data, or untangling prop-drilling and over-globalized state.
---

# State management

Stack-agnostic principles, concrete examples in React 19 and React Native.
The tools differ across ecosystems; the classification doesn't — every UI has
local, server, global, and URL state regardless of framework.

**Version targets:** React 19, React Native 0.81 (current stable), TanStack Query
v5, Zustand v5. Snippets grounded against Context7 (`/reactjs/react.dev`,
`/facebook/react-native`, `/tanstack/query`, `/pmndrs/zustand`) at authoring time —
see `references/snippets.md`.

## The core question

Every state decision reduces to: *who owns the source of truth, and who needs to
read it?* Answer those two and the **kind** of state — and therefore the tool —
falls out. Reaching for a global store first inverts this: it picks the tool
before classifying the state, and that's how a server response or a single
screen's toggle ends up in app-wide state it never needed.

## The kinds of state

Classify a piece of state before you pick where it lives:

- **Local** — owned by one component subtree, read only inside it. `useState` /
  `useReducer`. This is the default; most state is local.
- **Server cache** — a *copy* of data the server owns (the user, a list of todos,
  a profile). It belongs in a query library (TanStack Query, RTK Query, SWR), not
  a global store. It's a cache with its own lifecycle — stale, refetch, invalidate
  — not client state you mutate by hand.
- **Global client** — genuinely app-wide and client-owned: theme, auth session,
  feature flags, a cross-route cart. Context for low-frequency values; a
  selector-based store (Zustand) for anything that updates often.
- **URL** — state that should survive a reload and be shareable and bookmarkable:
  filters, the active tab, page number, a selected id. The router's params are the
  source of truth. On native, navigation route params + deep links play this role.
- **Derived** — anything computable from the above (a filtered list, a total, an
  `isValid` flag). Don't store it; compute it during render.

## Principles

- **Classify before you reach for a tool.** Name the kind of state first. The
  tool is a consequence of the classification, not the starting point.
- **Server data is a cache, not global state.** Most "global state" is server
  state wearing a Redux costume. A query library gives you caching, loading/error
  status, refetch, and invalidation for free; hand-rolling those into a global
  store reinvents it badly.
- **Colocate; lift to the lowest common owner — no higher.** State starts inside
  the component that uses it and moves up only to the closest shared ancestor.
  Lifting "just in case" creates prop-drilling and needless re-renders.
- **Derive, don't duplicate.** One source of truth; compute the rest. A `useEffect`
  that copies props or state into more state is almost always a derived value that
  should be computed during render instead.
- **Keep the global store small and selector-driven.** Global state is a cost:
  every consumer couples to it, and a careless selector re-renders half the app.
  Put only what's truly app-wide there, and subscribe to the narrowest slice.
- **Put shareable state in the URL.** If a user should be able to reload, or send a
  link, and land in the same place, the URL owns that state — not a component and
  not a store.
- **Mobile parity.** The same taxonomy holds on React Native. The differences:
  there's no URL bar (route params and deep links are the shareable-state channel),
  and server-cache refetch keys off navigation focus / app foreground, not window
  focus. See `references/pitfalls.md`.

## How to use this skill

1. Run **`references/checklist.md`** against the state you're adding or reviewing —
   it walks the classification and the per-kind traps.
2. Reach for a pattern in **`references/snippets.md`** (local + derived, server
   cache, global store, Context, URL, React Native refetch).
3. Check **`references/pitfalls.md`** before you ship — over-globalized state and
   server-data-in-a-store are the two most common review findings.

## Related

- Owning a single component's shape and prop surface → `component-design`
- The mechanics of fetching, caching, and loading/error states → `data-fetching`
- Form field state and validation → `forms-and-validation`
- Re-render cost from state and selectors → `frontend-performance`
