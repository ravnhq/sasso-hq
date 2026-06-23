# Animation and motion pitfalls

## Animating layout properties
**Symptom:** transitioning `width`, `height`, `top`/`left`, `margin`, or
`box-shadow` — the page relayouts and repaints every frame and visibly stutters.
**Fix:** animate `transform` and `opacity` only. For size/position changes use a
transform (scale/translate) or a FLIP approach (measure first + last, animate the
delta with `transform`).

## Ignoring reduced motion
**Symptom:** parallax, big slides, or auto-playing motion with no
`prefers-reduced-motion` / `AccessibilityInfo` handling — nauseating for
motion-sensitive users and a WCAG 2.3.3 failure.
**Fix:** gate via the CSS media query and/or a `useReducedMotion` hook
(see `references/snippets.md`).

## Reduced motion = *no* motion
**Symptom:** under reduced motion you disable everything, including the feedback
that tells the user their action registered.
**Fix:** reduce, don't strip. Replace large/translational/parallax motion with a
quick cross-fade or an instant state change; keep essential feedback.

## Missing `useNativeDriver` (or using it on layout props)
**Symptom:** RN animation runs on the JS thread and drops frames under load; or
`useNativeDriver: true` on `height`/`margin` throws or silently no-ops.
**Fix:** set `useNativeDriver: true` and animate only `transform`/`opacity`. For
layout, use Reanimated layout animations or `LayoutAnimation`.

## Per-frame `setState` animation
**Symptom:** an animation driven by `setState` inside `requestAnimationFrame`/
`setInterval` — React re-renders every frame and the GC thrashes.
**Fix:** animate outside React's render with CSS, the Web Animations API,
`Animated`, or Reanimated worklets.

## Too long / non-interruptible
**Symptom:** 500ms+ transitions that can't be canceled and queue up behind each
other, so the UI feels sluggish and unresponsive.
**Fix:** keep UI feedback ~150–300ms; make motion interruptible and cancel
in-flight animations when new input arrives.

## `will-change` left on everywhere
**Symptom:** `will-change: transform` declared statically on many elements to "make
it smooth" — each forces a compositor layer, blowing up memory and sometimes making
things slower.
**Fix:** use it sparingly, ideally set just before animating and removed after; let
the browser manage layers by default. (On RN the analogue is
`renderToHardwareTextureAndroid` for static, animated subtrees — also used sparingly.)
