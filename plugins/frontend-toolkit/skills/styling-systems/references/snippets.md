# Styling systems snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`) and React Native 0.81
> (`/facebook/react-native`). Re-ground and update these when you bump versions.

## Design tokens as the source of truth (web)

Define every system-owned value once as a CSS custom property. A two-tier setup —
a private raw palette exposed through *semantic* tokens — lets you re-theme without
touching components. Components read `var(--color-bg)`, never `#0f172a`.

```css
/* tokens.css — the single source of truth. Everything else references these. */
:root {
  /* Spacing: one 4px-step scale, not arbitrary px. */
  --space-1: 0.25rem;  /* 4px  */
  --space-2: 0.5rem;   /* 8px  */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */

  --font-sm: 0.875rem;
  --font-md: 1rem;
  --font-lg: 1.25rem;
  --radius-md: 0.5rem;

  /* Raw palette (private — don't use directly in components) */
  --blue-600: #2563eb;
  --red-600: #dc2626;
  --slate-900: #0f172a;
  --slate-0: #ffffff;

  /* Semantic tokens — what components actually use */
  --color-bg: var(--slate-0);
  --color-text: var(--slate-900);
  --color-accent: var(--blue-600);
  --color-danger: var(--red-600);
}

/* Dark theme: same names, different values. No component changes. */
[data-theme="dark"] {
  --color-bg: var(--slate-900);
  --color-text: var(--slate-0);
}
```

## Consuming tokens: static in `className`, variants enumerated (web)

Static look lives in a class that reads tokens. Variants are an enumerated prop,
not an open style hole; conditional classes use the `classnames` pattern. Only the
genuinely dynamic value (a runtime width) goes in inline `style`.

```tsx
import cn from "classnames";
import styles from "./Button.module.css";

type ButtonProps = {
  variant?: "primary" | "danger";
  size?: "sm" | "md";
  pending?: boolean;
  children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

function Button({ variant = "primary", size = "md", pending, children, ...rest }: ButtonProps) {
  return (
    <button
      className={cn(styles.button, styles[variant], styles[size], { [styles.pending]: pending })}
      {...rest}
    >
      {children}
    </button>
  );
}

// Inline style only for a value computed at runtime — here, a dynamic width.
function Progress({ percent }: { percent: number }) {
  return (
    <div className={styles.track}>
      <div className={styles.fill} style={{ width: `${percent}%` }} />
    </div>
  );
}
```

```css
/* Button.module.css — reads tokens, never raw values. */
.button {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-md);
  background: var(--color-accent);
  color: var(--color-bg);
}
.danger { background: var(--color-danger); }
.sm { padding: var(--space-1) var(--space-2); font-size: var(--font-sm); }
.pending { opacity: 0.6; pointer-events: none; }
```

## Theme toggle: default to OS, allow override (web)

One source of truth — the `data-theme` attribute on `<html>` — drives every token
from `tokens.css`. Default to the OS preference; let the user override.

```tsx
import { useEffect, useState } from "react";

type Theme = "light" | "dark";

function useTheme(): [Theme, (t: Theme) => void] {
  const [theme, setTheme] = useState<Theme>("light"); // stable default (SSR-safe)

  // Adopt the OS preference on the client, and follow later changes.
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    setTheme(mq.matches ? "dark" : "light");
    const onChange = (e: MediaQueryListEvent) => setTheme(e.matches ? "dark" : "light");
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  // One source of truth: the data-theme attribute drives every token.
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return [theme, setTheme];
}
```

## React Native: tokens as a typed object + `StyleSheet`

RN has no CSS variables, so tokens are a typed object. `StyleSheet.create` is the
`className` equivalent: styles are created once, not re-allocated per render.

```tsx
// tokens.ts
export const tokens = {
  space: { 1: 4, 2: 8, 4: 16, 6: 24 },
  radius: { md: 8 },
  font: { sm: 14, md: 16, lg: 20 },
} as const;
```

```tsx
import { StyleSheet, Text, View } from "react-native";
import { tokens } from "./tokens";

const styles = StyleSheet.create({
  card: {
    padding: tokens.space[4],
    borderRadius: tokens.radius.md,
    gap: tokens.space[2],
  },
  title: { fontSize: tokens.font.lg },
});

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {children}
    </View>
  );
}
```

## React Native: theming via `useColorScheme` + context

`useColorScheme()` returns `'light' | 'dark'` and re-renders on OS theme change.
The provider swaps token *values* behind one stable shape; components read names.
Color tokens are theme-dependent (dynamic), so they go in inline `style`; static
layout stays in `StyleSheet`.

```tsx
import { createContext, useContext } from "react";
import { StyleSheet, Text, View, useColorScheme } from "react-native";

const lightColors = { bg: "#ffffff", text: "#0f172a", accent: "#2563eb" };
const darkColors = { bg: "#0f172a", text: "#ffffff", accent: "#60a5fa" };
type ThemeColors = typeof lightColors;

const ThemeContext = createContext<ThemeColors>(lightColors);
const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const scheme = useColorScheme();
  const colors = scheme === "dark" ? darkColors : lightColors;
  return <ThemeContext.Provider value={colors}>{children}</ThemeContext.Provider>;
}

const styles = StyleSheet.create({
  banner: { padding: 16, borderRadius: 8 },
});

function Banner({ children }: { children: React.ReactNode }) {
  const c = useTheme();
  return (
    <View style={[styles.banner, { backgroundColor: c.bg }]}>
      <Text style={{ color: c.text }}>{children}</Text>
    </View>
  );
}
```
