# Component design checklist

Run this against any component you create or review.

## Ownership
- [ ] Does this component own state/behavior, or is it just rendering parent data? (If the latter, should it be a prop or child instead?)
- [ ] Is each piece of state at the lowest common owner — not lifted "just in case"?
- [ ] Is there exactly one source of truth for each value it renders? (No state copied to fix a render.)

## Prop surface
- [ ] Are there ≤ ~5 meaningful props? More usually means split or compose.
- [ ] Are boolean flags (`isX`, `showY`) multiplying? Prefer `children`/slots.
- [ ] Are prop names honest about what they do (no leaked internals)?
- [ ] Are required vs optional props clear, with sensible defaults?
- [ ] Is each value deliberately controlled (prop) or uncontrolled (state) — not accidental?

## Composition
- [ ] Could a config-heavy component be expressed as composition (`children`, compound components)?
- [ ] Is data-fetching separated from presentation?
- [ ] Is the component reusable without its current parent's context?

## React Native parity (if applicable)
- [ ] Are list item components cheap — wrapped in `React.memo`, with stable callbacks and no inline allocation per render?
- [ ] Does the list pass `keyExtractor`, and `extraData` for anything the item depends on outside `data`?
- [ ] Primitives correct (`View`/`Text`/`Pressable`, not web `div`/`span`)?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (state → `state-management`, styling → `styling-systems`, a11y → `accessibility-audit`.)
