# Native performance snippets

> Grounded against Context7: React 19 + React Compiler (`/reactjs/react.dev`) and
> React Native 0.81 on the New Architecture (`/facebook/react-native`). Re-ground
> and update these when you bump versions.

## A virtualized list done right (FlatList)

`FlatList` mounts only the visible window and is a `PureComponent` — it re-renders
a row only when that row's props change by shallow comparison. So keep row props
`===`-stable (memoized row + hoisted callback), give it a stable `keyExtractor`,
and pass `extraData` for anything a row reads outside `data` (here, the selection).
For fixed-height rows, `getItemLayout` lets the list skip measurement entirely.

```tsx
import { memo, useCallback, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text } from "react-native";

type Row = { id: string; title: string };
const ITEM_HEIGHT = 56;

const ListRow = memo(function ListRow({
  item, selected, onPress,
}: { item: Row; selected: boolean; onPress: (id: string) => void }) {
  return (
    <Pressable style={styles.row} onPress={() => onPress(item.id)}>
      <Text style={selected ? styles.selected : styles.label}>{item.title}</Text>
    </Pressable>
  );
});

function SelectableList({ data }: { data: Row[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // Stable identity so memoized rows don't re-render on every parent render.
  const onPress = useCallback((id: string) => setSelectedId(id), []);

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      extraData={selectedId}
      getItemLayout={(_, index) => ({ length: ITEM_HEIGHT, offset: ITEM_HEIGHT * index, index })}
      initialNumToRender={10}
      windowSize={11}
      renderItem={({ item }) => (
        <ListRow item={item} selected={item.id === selectedId} onPress={onPress} />
      )}
    />
  );
}

// Module-level styles: the style objects keep one identity across renders.
const styles = StyleSheet.create({
  row: { height: ITEM_HEIGHT, justifyContent: "center", paddingHorizontal: 16 },
  label: { fontWeight: "normal" },
  selected: { fontWeight: "bold" },
});
```

## FlashList — a recycling upgrade

```tsx
// Shopify's FlashList recycles row views instead of mounting one per item, which
// usually beats FlatList on long or heterogeneous lists. The data/renderItem API
// is near-identical, so migration is mostly a swap. Ground the current FlashList
// API against Context7 before adopting — its props evolve faster than RN core.
import { FlashList } from "@shopify/flash-list";

<FlashList
  data={data}
  keyExtractor={(item) => item.id}
  extraData={selectedId}
  renderItem={({ item }) => (
    <ListRow item={item} selected={item.id === selectedId} onPress={onPress} />
  )}
/>;
```

## Render cost: memoize the expensive child (and when not to)

```tsx
// Manual memoization (React 18, or React 19 not yet on the compiler): `memo` skips
// the child when props are ===-stable; `useMemo`/`useCallback` keep them stable.
import { memo, useCallback, useMemo } from "react";

const Chart = memo(function Chart({ points, onSelect }: {
  points: Point[]; onSelect: (id: string) => void;
}) {
  return <Canvas points={points} onSelect={onSelect} />; // ...expensive render...
});

function Dashboard({ raw, productId }: { raw: Sample[]; productId: string }) {
  const points = useMemo(() => downsample(raw), [raw]);                  // cache the computation
  const onSelect = useCallback((id: string) => track(productId, id), [productId]); // stable identity
  return <Chart points={points} onSelect={onSelect} />;
}
```

> On **React 19 with the React Compiler**, delete this hand-memoization: the
> compiler inserts the equivalent automatically, so `Dashboard` stays plain and
> still skips the re-render. Reach for manual `memo`/`useMemo`/`useCallback` only
> where you're not on the compiler, or where profiling shows a specific hot spot.

## Bridge cost: keep scroll-linked values off the JS thread

```tsx
// WRONG: every scroll frame crosses native→JS and re-renders the tree.
function ParallaxHeader() {
  const [y, setY] = useState(0);
  return (
    <Animated.ScrollView
      onScroll={(e) => setY(e.nativeEvent.contentOffset.y)} // setState per frame → jank
      scrollEventThrottle={16}
    >
      {/* a header transformed from `y` re-renders on every scrolled pixel */}
    </Animated.ScrollView>
  );
}
```

```tsx
// RIGHT: the offset lives in an Animated.Value driven on the native thread.
// useNativeDriver: true means the scroll never round-trips through JS state.
import { Animated } from "react-native";
import { useRef } from "react";

function ParallaxHeader() {
  const y = useRef(new Animated.Value(0)).current;
  const onScroll = Animated.event([{ nativeEvent: { contentOffset: { y } } }], {
    useNativeDriver: true,
  });
  const translateY = y.interpolate({
    inputRange: [0, 200], outputRange: [0, -100], extrapolate: "clamp",
  });

  return (
    <Animated.ScrollView onScroll={onScroll} scrollEventThrottle={16}>
      <Animated.View style={{ transform: [{ translateY }] }}>{/* header */}</Animated.View>
    </Animated.ScrollView>
  );
}
```

> For anything beyond simple interpolations, **`react-native-reanimated`** runs the
> whole animation on the UI thread via worklets — see `animation-and-motion`.

## Keep the JS thread free: defer non-urgent work

```tsx
// Typing stays responsive: the heavy filtered list updates at a lower priority.
import { useDeferredValue, useMemo, useState } from "react";
import { TextInput } from "react-native";

function Search({ items }: { items: Item[] }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);            // lags behind during fast input
  const results = useMemo(() => filter(items, deferredQuery), [items, deferredQuery]);
  return (
    <>
      <TextInput value={query} onChangeText={setQuery} />
      <ResultsList data={results} />
    </>
  );
}
```

> On native, wrap post-transition work in `InteractionManager.runAfterInteractions`
> so it waits for gestures and navigation to settle before running.
