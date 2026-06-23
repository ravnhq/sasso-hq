---
name: styling-systems
description: Apply design tokens and a coherent styling architecture — one source of truth for color, spacing, type, and theming — instead of ad-hoc CSS and magic numbers. Use when setting up styling for a new app, taming scattered or duplicated styles, building a light/dark theme, choosing a styling approach (CSS Modules, utility classes, CSS-in-JS, RN StyleSheet), or reviewing styling architecture.
---

# Styling systems

Stack-agnostic principles, concrete examples in React 19 (web) and React Native.
The token discipline ports to any styling tool — Tailwind, CSS Modules,
vanilla-extract, StyleSheet; the architecture doesn't change.

**Version targets:** React 19, React Native 0.81 (current stable; same APIs under
Expo). Snippets grounded against Context7 (`/reactjs/react.dev`,
`/facebook/react-native`) at authoring time — see `references/snippets.md`.

## The core question

Every styling decision reduces to: *is this value a decision the design system
already made, or one this component is making locally?* A color, space, or font
size the system owns belongs to a **named token**; a genuine one-off can stay
local. Ad-hoc CSS is what happens when system-owned values get retyped as literals
in 40 places.

## Principles

- **Tokens are the single source of truth.** Color, spacing, typography, radii,
  shadows, and z-index live as named tokens, not literals scattered across
  components. Change the token, not every call site.
- **Compose from a scale; don't free-type values.** Spacing and type come from a
  small fixed scale (e.g. a 4px step). A value that isn't on the scale is a
  missing token or a mistake — decide which, don't invent a new magic number.
- **Theme by swapping token values, not by forking components.** Light/dark (and
  brand) themes are the same components reading the same token *names*; only the
  values behind the names change. On web that's CSS custom properties; in RN it's
  a theme object behind context.
- **`className` for static, inline `style` only for dynamic.** Static look belongs
  in classes (or `StyleSheet` objects) — cheaper and cacheable. Reserve the inline
  `style` prop for values you compute at runtime. (React recommends exactly this.)
- **Expose intent, not a style hole.** A component's variants are an enumerated
  prop (`variant="danger"`, `size="sm"`), not an open `className`/`style`
  pass-through. Only true primitives expose styling hooks; higher-level components
  own their look.
- **Pick one mechanism per surface and commit.** CSS Modules, utility classes,
  CSS-in-JS, or RN `StyleSheet` — each is fine. Three mixed in one app is the
  problem. Decide per platform and make it the default.
- **Mobile parity.** RN has no cascade and no CSS variables; tokens are a plain
  typed object and `StyleSheet.create` is the `className` equivalent. The
  discipline is identical; only the transport differs. See `references/pitfalls.md`.
- **Show visual choices, don't describe them.** When a decision is genuinely
  visual — which palette, theme, or spacing scale — render the options for the user
  with the brainstorming **visual companion** (`superpowers:brainstorming`) and let
  them click, instead of asking in prose. "Which of these feels right?" is for the
  companion; "what should this do?" stays in the terminal.

## How to use this skill

1. Run **`references/checklist.md`** against the styling you're setting up or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (tokens, CSS-variable theming,
   variant props, RN tokens + `StyleSheet`, RN theming via context).
3. Check **`references/pitfalls.md`** before you ship — most styling PRs hit at least one.

## Related

- The component being styled → `component-design`
- State that drives a theme toggle → `state-management`
- Motion tokens and transitions → `animation-and-motion`
- Color contrast and focus styles → `accessibility-audit`
- Style cost in big lists / re-renders → `frontend-performance` (web), `native-performance` (RN)
- Comparing visual options with the user → `superpowers:brainstorming` (visual companion)
