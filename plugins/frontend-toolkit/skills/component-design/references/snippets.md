# Component design snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`) and React Native 0.81
> (`/facebook/react-native`). Re-ground and update these when you bump versions.

## Compose over configure (children + slots)

A `Card` that takes `children` (and optional slots) instead of a growing list of
`title`/`subtitle`/`footer`/`show*` props. The parent decides what goes inside.

```tsx
type CardProps = {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
};

function Card({ header, footer, children }: CardProps) {
  return (
    <div className="card">
      {header && <div className="card__header">{header}</div>}
      <div className="card__body">{children}</div>
      {footer && <div className="card__footer">{footer}</div>}
    </div>
  );
}

// Usage — composition, not configuration:
<Card header={<h3>Katsuko Saruhashi</h3>} footer={<a href="/more">More</a>}>
  <Avatar size={100} person={person} />
</Card>;
```

## Compound components (shared state via context)

When several sub-components must coordinate (a tab list and its panels), share
state through context instead of drilling props. The public API stays declarative.

```tsx
import { createContext, useContext, useState } from "react";

type TabsContextValue = { selected: string; select: (id: string) => void };
const TabsContext = createContext<TabsContextValue | null>(null);

function useTabs() {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("Tabs.* must render inside <Tabs>");
  return ctx;
}

function Tabs({ defaultId, children }: { defaultId: string; children: React.ReactNode }) {
  const [selected, setSelected] = useState(defaultId);
  return (
    <TabsContext.Provider value={{ selected, select: setSelected }}>
      {children}
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: React.ReactNode }) {
  return <div role="tablist">{children}</div>;
}

function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const { selected, select } = useTabs();
  return (
    <button role="tab" aria-selected={selected === id} onClick={() => select(id)}>
      {children}
    </button>
  );
}

function TabPanel({ id, children }: { id: string; children: React.ReactNode }) {
  const { selected } = useTabs();
  return selected === id ? <div role="tabpanel">{children}</div> : null;
}

Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage:
<Tabs defaultId="about">
  <Tabs.List>
    <Tabs.Tab id="about">About</Tabs.Tab>
    <Tabs.Tab id="etymology">Etymology</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="about">Almaty is Kazakhstan's largest city.</Tabs.Panel>
  <Tabs.Panel id="etymology">From алма, the Kazakh word for "apple".</Tabs.Panel>
</Tabs>;
```

## Controlled vs uncontrolled

The same `Panel` as uncontrolled (owns `isActive`) and controlled (parent owns it).
Uncontrolled drops in with less wiring; controlled lets a parent coordinate siblings
(e.g. an accordion where only one panel is open).

```tsx
import { useState } from "react";

// Uncontrolled: owns its own open state.
function UncontrolledPanel({ title, children }: { title: string; children: React.ReactNode }) {
  const [isActive, setIsActive] = useState(false);
  return (
    <section className="panel">
      <h3>{title}</h3>
      {isActive ? <p>{children}</p> : <button onClick={() => setIsActive(true)}>Show</button>}
    </section>
  );
}

// Controlled: parent drives `isActive` via props.
function Panel({
  title, children, isActive, onShow,
}: { title: string; children: React.ReactNode; isActive: boolean; onShow: () => void }) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      {isActive ? <p>{children}</p> : <button onClick={onShow}>Show</button>}
    </section>
  );
}

// Parent coordinates: only one panel open at a time.
function Accordion() {
  const [activeIndex, setActiveIndex] = useState(0);
  return (
    <>
      <Panel title="About" isActive={activeIndex === 0} onShow={() => setActiveIndex(0)}>
        Almaty is Kazakhstan's largest city.
      </Panel>
      <Panel title="Etymology" isActive={activeIndex === 1} onShow={() => setActiveIndex(1)}>
        From алма, the Kazakh word for "apple".
      </Panel>
    </>
  );
}
```

## React Native: a cheap list item

`FlatList` is a `PureComponent`: it re-renders an item only when that item's props
change by shallow comparison. Keep item props `===`-stable (memoized component +
stable callbacks), pass `keyExtractor`, and use `extraData` for anything the item
reads that isn't in `data` (e.g. the current selection).

```tsx
import { memo, useCallback, useState } from "react";
import { FlatList, Pressable, Text } from "react-native";

type Item = { id: string; title: string };

const ListItem = memo(function ListItem({
  item, selected, onPress,
}: { item: Item; selected: boolean; onPress: (id: string) => void }) {
  return (
    <Pressable onPress={() => onPress(item.id)}>
      <Text style={{ fontWeight: selected ? "bold" : "normal" }}>{item.title}</Text>
    </Pressable>
  );
});

function SelectableList({ data }: { data: Item[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // Stable identity so memoized items don't re-render every parent render.
  const onPress = useCallback((id: string) => setSelectedId(id), []);

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      extraData={selectedId}
      renderItem={({ item }) => (
        <ListItem item={item} selected={item.id === selectedId} onPress={onPress} />
      )}
    />
  );
}
```
