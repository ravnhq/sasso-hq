# Touch interaction snippets

> Grounded against Context7: react-native-gesture-handler 2.x
> (`/websites/swmansion_react-native-gesture-handler`) and react-native-reanimated
> 3.x/4.x (`/websites/swmansion_react-native-reanimated`), targeting React Native
> 0.81 / Expo SDK 54. The web snippet uses the W3C Pointer Events API + CSS
> `touch-action` (platform standards) with React 19 DOM handlers. Re-ground and
> update these when you bump versions.
>
> Native snippets assume the app root is wrapped in `<GestureHandlerRootView>` —
> without it, gestures silently never fire (see `references/pitfalls.md`).

## Tap vs double-tap (disambiguation with Exclusive)

`Exclusive` gives the double-tap priority: the single-tap only fires once it's clear
no second tap is coming. Without it the single-tap fires on the first touch and the
double-tap never gets a chance. Gesture callbacks are workletized when Reanimated is
installed, so hop to JS with `runOnJS` for navigation/`setState`.

```tsx
import { View } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { runOnJS } from "react-native-reanimated";

function PhotoTile({ onOpen, onLike }: { onOpen: () => void; onLike: () => void }) {
  const singleTap = Gesture.Tap().onStart(() => runOnJS(onOpen)());
  const doubleTap = Gesture.Tap()
    .numberOfTaps(2)
    .onStart(() => runOnJS(onLike)());

  return (
    <GestureDetector gesture={Gesture.Exclusive(doubleTap, singleTap)}>
      <View style={{ width: 300, height: 300 }} />
    </GestureDetector>
  );
}
```

## A drag that tracks the finger on the UI thread

Position lives in shared values updated inside the `onUpdate` worklet, so the card
follows the finger at the display's refresh rate even when the JS thread is busy.
Saving the start offset in `onBegin` lets successive drags accumulate; on release it
springs home.

```tsx
import { StyleSheet } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from "react-native-reanimated";

function DraggableCard() {
  const offsetX = useSharedValue(0);
  const offsetY = useSharedValue(0);
  const startX = useSharedValue(0);
  const startY = useSharedValue(0);
  const pressed = useSharedValue(false);

  const pan = Gesture.Pan()
    .onBegin(() => {
      startX.value = offsetX.value;
      startY.value = offsetY.value;
      pressed.value = true;
    })
    .onUpdate((e) => {
      offsetX.value = startX.value + e.translationX;
      offsetY.value = startY.value + e.translationY;
    })
    .onFinalize(() => {
      offsetX.value = withSpring(0);
      offsetY.value = withSpring(0);
      pressed.value = false;
    });

  const style = useAnimatedStyle(() => ({
    transform: [
      { translateX: offsetX.value },
      { translateY: offsetY.value },
      { scale: withSpring(pressed.value ? 1.05 : 1) },
    ],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.card, style]} />
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  card: { width: 120, height: 120, borderRadius: 16, backgroundColor: "#4f46e5" },
});
```

## Swipe-to-action without stealing the scroll

`activeOffsetX` only claims the gesture after ~10px of horizontal movement;
`failOffsetY` bails the instant the finger drifts vertically, leaving a near-vertical
drag to the surrounding `FlatList`. Without these thresholds the row swallows every
scroll attempt. The release worklet animates out, then `runOnJS` fires the action.

```tsx
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  runOnJS,
} from "react-native-reanimated";

function SwipeToDeleteRow({
  onDelete,
  children,
}: {
  onDelete: () => void;
  children: React.ReactNode;
}) {
  const x = useSharedValue(0);

  const pan = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .failOffsetY([-8, 8])
    .onUpdate((e) => {
      x.value = Math.min(0, e.translationX); // left-swipe only
    })
    .onEnd(() => {
      if (x.value < -120) {
        x.value = withTiming(-400, undefined, () => runOnJS(onDelete)());
      } else {
        x.value = withTiming(0);
      }
    });

  const style = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={style}>{children}</Animated.View>
    </GestureDetector>
  );
}
```

## A sized target with instant feedback (Pressable + hitSlop)

The glyph is small but the target is ≥44×44 via `minWidth`/`minHeight`, and
`hitSlop` forgives another 8px beyond the visual bounds. Feedback is immediate
because the `pressed` style applies on touch-down. The a11y props keep it usable
with a screen reader.

```tsx
import { Pressable, Text, StyleSheet } from "react-native";

function IconButton({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Pressable
      onPress={onPress}
      hitSlop={8}
      accessibilityRole="button"
      accessibilityLabel={label}
      style={({ pressed }) => [styles.button, pressed && styles.pressed]}
    >
      <Text style={styles.glyph}>★</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: { minWidth: 44, minHeight: 44, alignItems: "center", justifyContent: "center" },
  pressed: { opacity: 0.6 },
  glyph: { fontSize: 20 },
});
```

## Web: a finger-tracking drag with Pointer Events

Pointer Events unify mouse/touch/pen. `setPointerCapture` keeps delivering
move/up to this element even when the finger slides outside it; `touch-action: none`
tells the browser we own the gesture, so it won't scroll or fire the ~300ms tap
delay. For very hot drags, write `el.style.transform` directly off a ref to skip a
React render per move.

```tsx
import { useRef, useState } from "react";

function DraggableBox() {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const start = useRef({ x: 0, y: 0, px: 0, py: 0 });
  const dragging = useRef(false);

  return (
    <div
      onPointerDown={(e) => {
        dragging.current = true;
        start.current = { x: pos.x, y: pos.y, px: e.clientX, py: e.clientY };
        e.currentTarget.setPointerCapture(e.pointerId);
      }}
      onPointerMove={(e) => {
        if (!dragging.current) return;
        setPos({
          x: start.current.x + (e.clientX - start.current.px),
          y: start.current.y + (e.clientY - start.current.py),
        });
      }}
      onPointerUp={() => {
        dragging.current = false;
      }}
      style={{
        touchAction: "none",
        transform: `translate(${pos.x}px, ${pos.y}px)`,
        width: 120,
        height: 120,
        borderRadius: 16,
        background: "#4f46e5",
      }}
    />
  );
}
```
