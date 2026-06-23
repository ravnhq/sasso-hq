# Styling systems pitfalls

## Magic numbers instead of tokens
**Symptom:** `padding: 13px`, `color: #3b82f6` sprinkled across components; a brand
tweak becomes a find-and-replace.
**Fix:** define the value once as a token; reference it everywhere. A value worth
using twice is worth a name.

## Off-the-scale values
**Symptom:** spacing like `7px`, `11px`, `19px` — every component slightly different.
**Fix:** snap to the spacing/type scale. If nothing fits, the scale is wrong or you
need a new token — decide deliberately, don't free-type.

## Theming by forking components
**Symptom:** `CardDark` / `CardLight`, or `if (isDark)` branches in render.
**Fix:** one component reads token *names*; the theme swaps the *values* (CSS custom
properties on web, a theme object behind context in RN).

## Hard-coded colors that ignore the theme
**Symptom:** a literal `background: #fff` survives the theme switch, so text vanishes
on dark.
**Fix:** route every surface/text color through a semantic token (`--color-bg`);
never hard-code colors at the call site.

## Mixed styling mechanisms
**Symptom:** Tailwind here, CSS-in-JS there, a stray inline `style`, plus a global
stylesheet — specificity wars and no one knows where a style lives.
**Fix:** pick one mechanism per platform and make it the default; migrate the
strays, don't add a fourth.

## `className`/`style` pass-through as an API
**Symptom:** every component takes `className`/`style` and spreads it, so callers
reach in and override anything.
**Fix:** expose intent, not raw styling — an enumerated `variant`/`size` prop. Only
true primitives expose styling hooks. (Same boundary as `component-design`.)

## Inline style for static look (web)
**Symptom:** `style={{ display: "flex", gap: 8 }}` for styling that never changes.
**Fix:** static look belongs in a class — cheaper and cacheable. Reserve inline
`style` for runtime-computed values. (React's own guidance.)

## Inline style objects in hot paths (RN)
**Symptom:** `style={{ padding: 16 }}` rebuilt every render inside a `FlatList` row →
allocation churn and lost memoization.
**Fix:** hoist static styles into `StyleSheet.create` (created once); keep only
genuinely dynamic values inline. (See `native-performance`.)
