# Frontend performance snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`), React Native 0.81
> (`/facebook/react-native`), and web-vitals v4+ (`/googlechrome/web-vitals`).
> Re-ground and update these when you bump versions.

Snippets share `type Item = { id: string; label: string }`.

## Measure Core Web Vitals from real users

You can't fix what you don't measure. The `web-vitals` library reports the three
Core Web Vitals as real users experience them. INP replaced FID in v4 — measure
`onINP`, not the retired `onFID`. Send with `sendBeacon` so the report survives the
page being unloaded.

```ts
import { onCLS, onINP, onLCP, type Metric } from "web-vitals";

function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({ name: metric.name, value: metric.value, id: metric.id });
  // sendBeacon survives page unload; fall back to fetch with keepalive.
  if (!navigator.sendBeacon?.("/analytics", body)) {
    fetch("/analytics", { body, method: "POST", keepalive: true });
  }
}

onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onLCP(sendToAnalytics);
```

For *why* a metric is bad (which element, which long task), import from
`web-vitals/attribution` — same functions, richer `metric.attribution`.

## Code-split: ship the heavy chunk only when it's needed

The cheapest bundle is the one you don't send. `lazy` + `Suspense` move a component
(and its heavy dependencies) into a separate chunk, fetched only when it first
renders. Do this per route and for big, below-the-fold, or rarely-used components.

```tsx
import { lazy, Suspense } from "react";

// `Chart` and everything it imports leave the initial bundle.
const Chart = lazy(() => import("./Chart"));

function Dashboard({ showChart }: { showChart: boolean }) {
  return (
    <section>
      <Summary />
      {showChart && (
        <Suspense fallback={<Spinner />}>
          <Chart />
        </Suspense>
      )}
    </section>
  );
}
```

## Keep input responsive under heavy updates

`useDeferredValue` lets the urgent update (the keystroke) commit immediately while
the expensive render (filtering a big list) trails behind on a copy React can
interrupt. The input stays snappy — this is the lever for a bad **INP**.

```tsx
import { useDeferredValue, useMemo, useState } from "react";

function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query); // trails `query`, interruptible
  const results = useMemo(
    () => items.filter((i) => i.label.includes(deferredQuery)),
    [items, deferredQuery],
  );
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <Results items={results} />
    </>
  );
}
```

For an imperative slow update (tab switch, navigation), mark it non-blocking with
`useTransition` instead — `startTransition` keeps the rest of the UI interactive:

```tsx
const [isPending, startTransition] = useTransition();
startTransition(() => setTab(nextTab)); // interruptible; show a pending state
```

## Skip unnecessary re-renders

When a profile shows a child re-rendering for no reason, wrap it in `memo` and keep
its props `===`-stable. `memo` only helps if the props don't change identity every
render — so hoist callbacks with `useCallback` and objects with `useMemo`.

```tsx
import { memo, useCallback, useState } from "react";

const ExpensiveList = memo(function ExpensiveList({
  items, onPick,
}: { items: Item[]; onPick: (id: string) => void }) {
  return <ul>{items.map((i) => <li key={i.id} onClick={() => onPick(i.id)}>{i.label}</li>)}</ul>;
});

function Page({ items }: { items: Item[] }) {
  const [, setSelected] = useState<string | null>(null);
  const onPick = useCallback((id: string) => setSelected(id), []); // stable identity
  return <ExpensiveList items={items} onPick={onPick} />;
}
```

**React Compiler (React 19):** when enabled, it inserts this memoization
automatically for code that follows the Rules of React — you can delete most manual
`memo`/`useMemo`/`useCallback`. Until it's on (or for code it can't prove safe), do
it by hand as above, and only where a profile shows a real cost.

## React Native: a virtualized, cheap list

Never render a long list with `.map()` inside a `ScrollView` — it mounts every row.
`FlatList` virtualizes (mounts only what's near the viewport). With fixed-height
rows, `getItemLayout` skips per-item measurement — a large win past a few hundred
rows. Keep rows `memo`'d with stable callbacks; `FlatList` is a `PureComponent`.

```tsx
import { memo, useCallback } from "react";
import { FlatList, Text, View } from "react-native";

const ROW_HEIGHT = 56;

const Row = memo(function Row({ item }: { item: Item }) {
  return (
    <View style={{ height: ROW_HEIGHT, justifyContent: "center" }}>
      <Text>{item.label}</Text>
    </View>
  );
});

function BigList({ data }: { data: Item[] }) {
  const renderItem = useCallback(({ item }: { item: Item }) => <Row item={item} />, []);
  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      getItemLayout={(_, index) => ({ length: ROW_HEIGHT, offset: ROW_HEIGHT * index, index })}
      initialNumToRender={10}
      maxToRenderPerBatch={10}
      windowSize={7}
    />
  );
}
```

Pass anything a row reads from outside `data` (e.g. the current selection) via
`extraData`, treated immutably, or the `PureComponent` won't re-render it. For very
large or variable-height lists, Shopify's `FlashList` is a near-drop-in with better
defaults. Deeper RN list/render/bridge tuning lives in `native-performance`.
