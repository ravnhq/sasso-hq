# Component design pitfalls

## Boolean prop explosion
**Symptom:** `<Modal isOpen isFullscreen showHeader showFooter hideClose ...>`.
**Fix:** compose — `<Modal><Modal.Header/>...</Modal>` — or split into variants.

## Premature state lifting
**Symptom:** state lives three levels up and is prop-drilled through components
that only pass it along.
**Fix:** move state down to the lowest common owner; if it's genuinely cross-cutting,
that's a `state-management` concern, not deeper drilling.

## God component
**Symptom:** one component fetches data, manages state, lays out, and styles.
**Fix:** split the data owner from the presentational shell; the shell takes props.

## Duplicated source of truth
**Symptom:** state copied into another `useState` to fix a stale render.
**Fix:** one source of truth; derive, don't copy.

## Accidental controlled/uncontrolled
**Symptom:** a component owns local state *and* accepts a prop for the same value,
so parent and child fight over it.
**Fix:** pick one per value. Controlled = prop + change handler; uncontrolled = state
+ optional `defaultValue`. Don't do both for the same field.

## RN: expensive list items
**Symptom:** janky `FlatList`; new closures/objects allocated per row, items
re-render on every parent render.
**Fix:** wrap the item in `React.memo`, hoist callbacks with `useCallback`, pass
`keyExtractor`, and use `extraData` for anything the item depends on outside `data`
(FlatList is a `PureComponent` and won't re-render otherwise).

## className/style pass-through on non-primitives
**Symptom:** every component accepts `className`/`style` and forwards it, leaking
layout control to callers.
**Fix:** only true primitives expose styling hooks; higher-level components own
their look. (Where styling *is* the concern, that's `styling-systems`.)
