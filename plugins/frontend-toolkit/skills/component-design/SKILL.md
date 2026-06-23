---
name: component-design
description: Design React-family and React Native components with clear composition, prop boundaries, and ownership — when to split, when to compose, what to lift, and what to keep local. Use when creating a new component, refactoring a bloated one, deciding a component's props/children API, or reviewing component structure.
---

# Component design

Stack-agnostic principles, concrete examples in React 19 and React Native.
The examples port to Vue/Svelte; the judgments don't change.

**Version targets:** React 19, React Native 0.81 (current stable). Snippets grounded
against Context7 (`/reactjs/react.dev`, `/facebook/react-native`) at authoring time —
see `references/snippets.md`.

## The core question

Every component decision reduces to: *what does this component own, and what does
it merely render?* Owned state and behavior justify a component; pure rendering of
parent-owned data is often a prop or a child, not a new component.

## Principles

- **Compose over configure.** Prefer `children` and slot props to a growing list
  of boolean flags. A component with eight `is*`/`show*` props is usually several
  components wearing a trench coat.
- **Lift state to its lowest common owner — no higher.** State lives at the
  closest ancestor that needs it. Lifting "just in case" creates prop-drilling
  and re-render cost.
- **Keep the public prop surface narrow and honest.** Props are an API. Fewer,
  well-named props beat many overlapping ones. Don't leak implementation (no
  `className`/`style` pass-through unless the component is genuinely a primitive).
- **Decide controlled vs uncontrolled deliberately.** Uncontrolled (owns its
  state) is easier to drop in; controlled (driven by props) is coordinable. Pick
  per piece of information, and say which in the prop names.
- **Separate layout from data.** A component that both fetches and lays out is
  hard to reuse and test. Split the data owner from the presentational shell.
- **Mobile parity.** The same ownership rules hold in React Native; the
  difference is primitives (`View`/`Text`/`Pressable`) and that list item
  components render many times, so they must be cheap. See `references/pitfalls.md`.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — which composition or layout — render the options for the user with the
  brainstorming **visual companion** (`superpowers:brainstorming`) and let them
  click, instead of asking in prose. "Which of these feels right?" is for the
  companion; "what should this do?" stays in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** against the component you're designing or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (composition, compound
   components, controlled/uncontrolled, RN list item).
3. Check **`references/pitfalls.md`** before you ship — most component PRs hit at least one.

## Related

- State that crosses components → `state-management`
- Styling the component → `styling-systems`
- Making it accessible → `accessibility-audit`
- Testing it by behavior → `frontend-testing`
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
