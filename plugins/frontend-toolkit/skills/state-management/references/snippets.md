# State management snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`), React Native 0.81
> (`/facebook/react-native`), TanStack Query v5 (`/tanstack/query`), and Zustand v5
> (`/pmndrs/zustand`). Re-ground and update these when you bump versions.

One snippet per kind of state, in the order you should consider them: local first,
then a server cache, then global client state, then the URL.

## Local first — derive, don't store

The default. Keep raw, owned values in `useState`; compute everything else during
render. A second `useState` (or a `useEffect`) that holds a "filtered" or "total"
copy is a derived value that can drift — don't create it.

```tsx
import { useState } from "react";

type Product = { id: string; name: string };

function ProductList({ products }: { products: Product[] }) {
  const [query, setQuery] = useState(""); // raw, owned state

  // Derived — computed in render, never stored. No second state, no sync effect.
  const visible = products.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase()),
  );
  // Wrap the filter in useMemo only if profiling shows it's hot.

  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search" />
      <ul>{visible.map((p) => <li key={p.id}>{p.name}</li>)}</ul>
    </>
  );
}
```

## Server state is a cache, not global state

Data the server owns belongs in a query cache, keyed and with loading/error status
built in — not in a global store you mutate by hand. Mutations invalidate the key
and let the cache refetch the source of truth. (For fetching/caching depth, see
`data-fetching`; this shows only that server state is its *own* kind.)

```tsx
import {
  QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient,
} from "@tanstack/react-query";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Todos />
    </QueryClientProvider>
  );
}

function Todos() {
  const qc = useQueryClient();

  // The cache owns server data: a stable queryKey + status flags, for free.
  const { data, isPending, isError } = useQuery({
    queryKey: ["todos"],
    queryFn: fetchTodos,
  });

  // Don't hand-edit a copy — invalidate the key; the cache refetches.
  const addTodo = useMutation({
    mutationFn: postTodo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["todos"] }),
  });

  if (isPending) return <Spinner />;
  if (isError) return <ErrorBanner />;

  return (
    <>
      <ul>{data.map((t) => <li key={t.id}>{t.title}</li>)}</ul>
      <button disabled={addTodo.isPending} onClick={() => addTodo.mutate({ title: "New" })}>
        Add
      </button>
    </>
  );
}
```

## Global client state — a selector store

For state that is *genuinely* app-wide and client-owned (theme, auth session,
feature flags). A selector store keeps consumers subscribed to the narrowest slice,
so an unrelated change doesn't re-render them. Actions live in the store.

```tsx
import { create } from "zustand";
import { useShallow } from "zustand/react/shallow";

type Theme = "light" | "dark";
type AppState = {
  theme: Theme;
  user: { id: string; name: string } | null;
  toggleTheme: () => void;
  signOut: () => void;
};

const useAppStore = create<AppState>()((set) => ({
  theme: "light",
  user: null,
  toggleTheme: () => set((s) => ({ theme: s.theme === "light" ? "dark" : "light" })),
  signOut: () => set({ user: null }),
}));

// Subscribe to one slice: this re-renders only when `theme` changes.
function ThemeToggle() {
  const theme = useAppStore((s) => s.theme);
  const toggleTheme = useAppStore((s) => s.toggleTheme);
  return <button onClick={toggleTheme}>Theme: {theme}</button>;
}

// Selecting several values? useShallow stops a fresh object re-rendering every time.
function UserBadge() {
  const { user, signOut } = useAppStore(
    useShallow((s) => ({ user: s.user, signOut: s.signOut })),
  );
  return user ? <button onClick={signOut}>{user.name}</button> : null;
}
```

## Shared low-frequency state — Context + useReducer

When a value is global but changes rarely (locale, a theme object), Context is
enough — no library. Pair it with `useReducer` for structured updates. Note the
trade-off: **any** Context value change re-renders every consumer (no selectors),
so reach for the store above when the value updates often.

```tsx
import { createContext, useContext, useReducer } from "react";

type State = { locale: string };
type Action = { type: "setLocale"; locale: string };

const SettingsContext = createContext<State | null>(null);
const SettingsDispatchContext = createContext<React.Dispatch<Action> | null>(null);

function settingsReducer(state: State, action: Action): State {
  switch (action.type) {
    case "setLocale":
      return { ...state, locale: action.locale };
  }
}

// React 19: render the context itself as the provider — no `.Provider`.
export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(settingsReducer, { locale: "en" });
  return (
    <SettingsContext value={state}>
      <SettingsDispatchContext value={dispatch}>{children}</SettingsDispatchContext>
    </SettingsContext>
  );
}

export const useSettings = () => useContext(SettingsContext)!;
export const useSettingsDispatch = () => useContext(SettingsDispatchContext)!;
```

## URL as the source of truth

State that should survive a reload and be shareable — filters, the active tab, a
selected id — belongs in the URL. Read it via subscription; don't mirror it into
component state that can drift. Routers (React Router's `useSearchParams`, Next.js,
Expo Router) ship typed wrappers; this shows the source of truth underneath them.

```tsx
import { useSyncExternalStore } from "react";

function useSearchParam(key: string): string | null {
  return useSyncExternalStore(
    (onChange) => {
      window.addEventListener("popstate", onChange);
      return () => window.removeEventListener("popstate", onChange);
    },
    () => new URLSearchParams(window.location.search).get(key),
  );
}

function setSearchParam(key: string, value: string) {
  const params = new URLSearchParams(window.location.search);
  if (value) params.set(key, value);
  else params.delete(key);
  window.history.pushState(null, "", `?${params}`);
  window.dispatchEvent(new PopStateEvent("popstate")); // notify subscribers
}

// The active tab lives in the URL — reload or share the link and it's restored.
function Tabs() {
  const tab = useSearchParam("tab") ?? "overview";
  return (
    <nav>
      <button aria-selected={tab === "overview"} onClick={() => setSearchParam("tab", "overview")}>
        Overview
      </button>
      <button aria-selected={tab === "details"} onClick={() => setSearchParam("tab", "details")}>
        Details
      </button>
    </nav>
  );
}
```

## React Native: refetch on focus, no URL bar

The taxonomy is identical on native, with two differences. Shareable/restorable
state lives in **navigation route params + deep links** (the URL equivalent — see
`mobile-navigation`). And the server cache can't key off window focus, because
there's no window: bridge `AppState` into TanStack Query's `focusManager` so it
refetches when the app returns to the foreground.

```tsx
import { useEffect } from "react";
import { AppState, Platform } from "react-native";
import type { AppStateStatus } from "react-native";
import { focusManager } from "@tanstack/react-query";

function onAppStateChange(status: AppStateStatus) {
  if (Platform.OS !== "web") focusManager.setFocused(status === "active");
}

// Mount once near the app root.
export function useAppFocusRefetch() {
  useEffect(() => {
    const sub = AppState.addEventListener("change", onAppStateChange);
    return () => sub.remove();
  }, []);
}
```
