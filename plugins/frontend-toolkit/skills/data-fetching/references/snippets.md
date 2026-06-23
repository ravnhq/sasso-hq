# Data fetching snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`), TanStack Query v5
> (`/tanstack/query`), and React Native 0.81 / Expo SDK 54 (`/facebook/react-native`).
> Re-ground and update these when you bump versions.

## React 19: `use()` + Suspense + Error Boundary

`use` reads a promise and suspends until it settles. A `<Suspense>` ancestor renders
the loading fallback; an error boundary catches rejection. Loading and error each live
in one place instead of being repeated as `if (loading)` / `if (error)` in every component.

```tsx
import { use, Suspense } from "react";
import { ErrorBoundary } from "react-error-boundary";

// The promise must be created *outside* this component (cache it / pass it as a prop).
// Creating a new promise here on every render would suspend forever.
function User({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise);
  return <h1>{user.name}</h1>;
}

function UserScreen({ userPromise }: { userPromise: Promise<User> }) {
  return (
    <ErrorBoundary fallback={<p>Couldn't load this user.</p>}>
      <Suspense fallback={<UserSkeleton />}>
        <User userPromise={userPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

## TanStack Query: a cached read with all four states

A query is identified by its `queryKey`: same key → shared, deduped, cached. `staleTime`
keeps fresh data from refetching on every mount. The `signal` aborts the request when the
key changes or the component unmounts. Render loading, error, empty, and success explicitly.

```tsx
import { useQuery } from "@tanstack/react-query";

function useUser(id: string) {
  return useQuery({
    queryKey: ["user", id],
    queryFn: ({ signal }) => fetchUser(id, signal),
    staleTime: 60_000, // treat data as fresh for 60s — don't refetch on every mount
  });
}

function UserCard({ id }: { id: string }) {
  const { data, isPending, isError, error, refetch } = useUser(id);

  if (isPending) return <UserSkeleton />;
  if (isError) return <ErrorRetry message={error.message} onRetry={() => refetch()} />;
  if (data.posts.length === 0) return <Empty>No posts yet.</Empty>;
  return <Profile user={data} />;
}
```

## TanStack Query: an optimistic mutation (update, roll back, reconcile)

Write to the cache immediately so the UI feels instant; snapshot the previous value so a
failed request can roll back; invalidate on settle so the cache re-syncs with the server.

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";

function useRenameUser(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => renameUser(id, name),
    onMutate: async (name) => {
      // Stop in-flight refetches so they can't clobber the optimistic value.
      await queryClient.cancelQueries({ queryKey: ["user", id] });
      const previous = queryClient.getQueryData<User>(["user", id]);
      queryClient.setQueryData<User>(["user", id], (u) => u && { ...u, name });
      return { previous }; // handed to onError for rollback
    },
    onError: (_err, _name, context) => {
      queryClient.setQueryData(["user", id], context?.previous);
    },
    onSettled: () => {
      // Re-sync with the server whether the mutation succeeded or failed.
      queryClient.invalidateQueries({ queryKey: ["user", id] });
    },
  });
}
```

## React Native: refetch on foreground + reconnect

React Native has no web window-focus or `navigator.onLine` events, so wire TanStack
Query's `focusManager` to `AppState` and its `onlineManager` to NetInfo. Do this once at
the app entry. Now cached screens refetch when the user returns to the app or the network
comes back — the mobile equivalent of stale-while-revalidate.

```tsx
import { useEffect } from "react";
import { AppState, type AppStateStatus, Platform } from "react-native";
import NetInfo from "@react-native-community/netinfo";
import { focusManager, onlineManager } from "@tanstack/react-query";

// Refetch when connectivity returns.
onlineManager.setEventListener((setOnline) =>
  NetInfo.addEventListener((state) => setOnline(!!state.isConnected)),
);

// Refetch when the app comes back to the foreground.
export function useRefetchOnForeground() {
  useEffect(() => {
    const sub = AppState.addEventListener("change", (status: AppStateStatus) => {
      if (Platform.OS !== "web") focusManager.setFocused(status === "active");
    });
    return () => sub.remove();
  }, []);
}
```
