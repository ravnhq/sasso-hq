# Styling systems checklist

Run this against the styling you're setting up or reviewing.

## Tokens
- [ ] Is every color / space / font-size / radius / shadow a named token, not a literal? (Grep the diff for hex colors and raw `px`.)
- [ ] Do spacing and type sizes come from one fixed scale, not arbitrary values?
- [ ] Is there exactly one definition of each token, with everything else referencing it (no copies)?
- [ ] At the point of use, are tokens semantic (`color-danger`, `space-md`) rather than raw (`red-600`, `8px`)?

## Theming
- [ ] Do light/dark (and brand) themes swap token *values* behind the same *names* — no forked or `if (isDark)` components?
- [ ] On web, are theme values CSS custom properties overridden under one scope (`[data-theme="dark"]` / `.dark`), not duplicated per component?
- [ ] In RN, is the theme one object behind context (or `useColorScheme`) that components read — not colors hard-coded per screen?
- [ ] Does the app default to the OS preference (`prefers-color-scheme` / `useColorScheme`)?

## Architecture
- [ ] Is there one chosen mechanism per platform (CSS Modules / utilities / CSS-in-JS / `StyleSheet`), used consistently — not three mixed?
- [ ] Is static styling in classes / `StyleSheet`, with inline `style` reserved for runtime-dynamic values?
- [ ] Are component variants an enumerated prop (`variant`, `size`) rather than an open `className`/`style` pass-through?
- [ ] Are reset / global styles isolated to one place, not sprinkled across components?

## React Native parity (if applicable)
- [ ] Are styles built with `StyleSheet.create` (created once), not fresh inline objects per render in list items / hot paths?
- [ ] Are tokens a typed JS/TS object, given RN has no CSS variables or cascade?
- [ ] Do pressable/stateful styles use the `style`-as-function form (`({ pressed }) => …`) instead of manual state?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (the component itself → `component-design`, motion tokens → `animation-and-motion`, contrast/focus → `accessibility-audit`, style cost in lists → `frontend-performance` / `native-performance`.)
