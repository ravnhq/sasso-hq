# Accessibility audit snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`) and React Native 0.81
> (`/facebook/react-native`), targeting WCAG 2.2 AA. Re-ground and update these
> when you bump versions.

## Labelled field with hint and error (web)

`useId` ties a `<label>`, its hint, and its error message to the input, so a
screen reader announces all three. `role="alert"` makes the error speak when it
appears (4.1.3); `aria-invalid` marks the field.

```tsx
import { useId } from "react";

function PasswordField({ error }: { error?: string }) {
  const id = useId();
  const hintId = `${id}-hint`;
  const errorId = `${id}-error`;
  return (
    <>
      <label htmlFor={id}>Password</label>
      <input
        id={id}
        type="password"
        aria-describedby={error ? `${hintId} ${errorId}` : hintId}
        aria-invalid={error ? true : undefined}
      />
      <p id={hintId}>At least 18 characters.</p>
      {error && <p id={errorId} role="alert">{error}</p>}
    </>
  );
}
```

## Icon-only button needs a name (web)

An icon button with no text announces only "button". Give it an `aria-label` and
hide the decorative glyph from AT (1.1.1, 4.1.2).

```tsx
// ❌ No accessible name.
<button onClick={onClose}><XIcon /></button>

// ✅ Name on the control; icon hidden from the accessibility tree.
<button aria-label="Close dialog" onClick={onClose}>
  <XIcon aria-hidden="true" />
</button>
```

## Focus management for a dialog (web)

Move focus into the dialog on open and restore it to the trigger on close, so
keyboard and screen-reader users aren't stranded (2.4.3, 2.1.2). React 19 passes
`ref` to function components as a plain prop, so a custom `<Dialog>` wrapper
wouldn't need `forwardRef`.

```tsx
import { useEffect, useRef } from "react";

function Dialog({ open, onClose, children }: {
  open: boolean; onClose: () => void; children: React.ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const restoreTo = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;
    restoreTo.current = document.activeElement as HTMLElement;
    ref.current?.focus();
    return () => restoreTo.current?.focus(); // restore focus to the trigger on close
  }, [open]);

  if (!open) return null;
  return (
    <div
      ref={ref}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={(e) => e.key === "Escape" && onClose()}
    >
      {children}
      {/* A production modal also traps Tab within the dialog — see pitfalls.md. */}
    </div>
  );
}
```

## Live region for async status (web)

`role="status"` is a polite live region (it implies `aria-live="polite"`), so
async results are announced without stealing focus (4.1.3). The container must
already be in the DOM before its text changes, or the update is missed — render it
always and swap the text.

```tsx
function SaveStatus({ status }: { status: "idle" | "saving" | "saved" | "error" }) {
  return (
    <p role="status">
      {status === "saving" && "Saving…"}
      {status === "saved" && "All changes saved."}
      {status === "error" && "Couldn't save. Retry."}
    </p>
  );
}
```

## React Native: role, name, and state on a control

Map the control to a native `accessibilityRole`, give it an `accessibilityLabel`,
and reflect its state via `accessibilityState`. `hitSlop` grows the touch target
toward 44pt without changing layout (2.5.8, 4.1.2).

```tsx
import { Pressable, Text } from "react-native";

function NotificationsToggle({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  return (
    <Pressable
      onPress={onToggle}
      accessibilityRole="switch"
      accessibilityLabel="Notifications"
      accessibilityState={{ checked: on }}
      hitSlop={8}
    >
      <Text>{on ? "On" : "Off"}</Text>
    </Pressable>
  );
}
```

## React Native: group a row into one element

Without `accessible`, a screen reader stops on every `Text` separately. Mark the
row `accessible` with one combined label so it's a single, sensible swipe.

```tsx
import { View, Text } from "react-native";

function ContactRow({ name, role }: { name: string; role: string }) {
  return (
    <View accessible accessibilityLabel={`${name}, ${role}`}>
      <Text>{name}</Text>
      <Text>{role}</Text>
    </View>
  );
}
```

## React Native: respect reduced motion, announce changes

Read and subscribe to the OS reduce-motion setting, and use
`announceForAccessibility` to report changes that don't move focus.

```tsx
import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";

function useReduceMotion() {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduce);
    const sub = AccessibilityInfo.addEventListener("reduceMotionChanged", setReduce);
    return () => sub.remove();
  }, []);
  return reduce;
}

// Speak a transient result without grabbing focus:
AccessibilityInfo.announceForAccessibility("Message sent");
```
