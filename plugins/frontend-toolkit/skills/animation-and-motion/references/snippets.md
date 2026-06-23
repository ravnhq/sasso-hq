# Animation and motion snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`), React Native 0.81
> (`/facebook/react-native`), Reanimated 4 (swmansion docs), and Motion
> (`motion.dev`, package `motion`, imported from `motion/react`). Re-ground and
> update these when you bump versions.

## Reduced motion as a primitive (web, React 19)

Everything below leans on this. Subscribe to the OS setting with
`useSyncExternalStore` so it stays correct if the user toggles it at runtime.
`subscribe`/`getSnapshot` live outside the component so React never resubscribes.

```tsx
import { useSyncExternalStore } from "react";

const QUERY = "(prefers-reduced-motion: reduce)";

function subscribe(onChange: () => void) {
  const mql = window.matchMedia(QUERY);
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}

const getSnapshot = () => window.matchMedia(QUERY).matches;
// SSR can't know the user's setting; assume motion is allowed and let the client
// correct on hydrate. Keep the real gate in CSS @media so it works without JS.
const getServerSnapshot = () => false;

export function useReducedMotion() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
```

## Compositor-only CSS, gated by `prefers-reduced-motion`

The cheapest correct animation: transition only `transform`/`opacity`, and
neutralize it in a reduced-motion block. This needs no JS and survives before
hydration — make it your baseline, reach for JS only when CSS can't express it.

```css
.card {
  transition: transform 200ms ease, opacity 200ms ease;
}
.card:hover {
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .card {
    transition: none; /* state still changes, just instantly */
  }
}
```

When the motion *is* JS-driven, branch on the hook — reduce, don't remove:

```tsx
function Toast({ message }: { message: string }) {
  const reduceMotion = useReducedMotion();
  return (
    <div
      className="toast"
      // A motion-sensitive user still gets the toast — it fades instead of sliding.
      style={{ animation: reduceMotion ? "toast-fade 120ms ease" : "toast-slide 220ms ease" }}
    >
      {message}
    </div>
  );
}
```

## Motion (library): let the config handle reduced motion

For richer web animation, Motion (`motion/react`, formerly Framer Motion) is the
ecosystem standard. `MotionConfig reducedMotion="user"` auto-disables transform and
layout animations when the OS setting is on while still allowing opacity — so you
write one declarative animation and don't branch per component.

```tsx
import { MotionConfig, motion } from "motion/react"; // was "framer-motion"

export function App({ children }: { children: React.ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}

function Drawer({ open }: { open: boolean }) {
  return (
    <motion.aside
      animate={{ x: open ? 0 : "-100%", opacity: open ? 1 : 0 }}
      transition={{ duration: 0.2 }}
    />
  );
}
```

## React Native: `Animated` on the native driver

`useNativeDriver: true` runs the animation on the UI thread, so JS-thread work
never stalls it. The native driver supports only `transform` and `opacity` — not
layout props like `height`/`margin` (for those, use Reanimated layout animations or
`LayoutAnimation`).

```tsx
import { useEffect, useRef } from "react";
import { Animated, Easing } from "react-native";

function FadeInUp({ children }: { children: React.ReactNode }) {
  const progress = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(progress, {
      toValue: 1,
      duration: 250,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, [progress]);

  return (
    <Animated.View
      style={{
        opacity: progress,
        transform: [
          { translateY: progress.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) },
        ],
      }}
    >
      {children}
    </Animated.View>
  );
}
```

## React Native: reduced motion

Mirror of the web hook, backed by the OS accessibility setting. Read it once and
subscribe to `reduceMotionChanged` so it stays live.

```tsx
import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";

export function useReducedMotion() {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduce);
    const sub = AccessibilityInfo.addEventListener("reduceMotionChanged", setReduce);
    return () => sub.remove();
  }, []);
  return reduce;
}
```

If you use **Reanimated 4**, you mostly don't need the gate: `withTiming`/`withSpring`
default to `reduceMotion: ReduceMotion.System`, so they already honor the device
setting. Use its `useReducedMotion()` hook only when you want to *choose a different*
animation rather than disable one.

```tsx
// `Animated` is the default export; the hooks and presets are named exports.
import Animated, { useReducedMotion, FadeIn, BounceIn, ReduceMotion } from "react-native-reanimated";

function Card({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion();
  // Keep a gentle fade for reduced motion; a playful bounce otherwise.
  const entering = reduce ? FadeIn.reduceMotion(ReduceMotion.Never) : BounceIn;
  return <Animated.View entering={entering}>{children}</Animated.View>;
}
```
