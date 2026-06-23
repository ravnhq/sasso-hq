# Frontend testing snippets

> Grounded against Context7: React Testing Library + user-event + jest-dom
> (`/testing-library/testing-library-docs`), React Native Testing Library
> (`/callstack/react-native-testing-library`), and MSW v2 (`/mswjs/mswjs.io`).
> Re-ground and update these when you bump versions.
>
> **Version targets:** React 19, `@testing-library/react` 16, `@testing-library/user-event` 14,
> `@testing-library/jest-dom` 6, React Native Testing Library 13 (matchers built in),
> MSW 2. Examples run under Vitest 3 or Jest 29+ — swap `vi.fn()` for `jest.fn()` accordingly.

## Behavior-first component test

Render, find the control the way a user would (role + accessible name), drive it
with `user-event`, and assert on the visible outcome — never on internal state.

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import { Disclosure } from "./Disclosure";

test("reveals the details when the user expands it", async () => {
  const user = userEvent.setup();
  render(<Disclosure title="Shipping">Ships in 2–3 days.</Disclosure>);

  // queryBy* for "should not be there yet" — assert behavior, not internal state.
  expect(screen.queryByText("Ships in 2–3 days.")).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "Shipping" }));

  expect(screen.getByText("Ships in 2–3 days.")).toBeVisible();
});
```

## A user flow across components

A flow exercises several units wired together. Find inputs by their label, type
with `user-event`, submit, and assert the resulting screen. `findBy*` waits for the
post-submit UI.

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import { SignInForm } from "./SignInForm";

test("user signs in and sees a welcome message", async () => {
  const user = userEvent.setup();
  const onSignIn = vi.fn(); // jest.fn() under Jest
  render(<SignInForm onSignIn={onSignIn} />);

  await user.type(screen.getByLabelText("Email"), "ada@example.com");
  await user.type(screen.getByLabelText("Password"), "lovelace");
  await user.click(screen.getByRole("button", { name: "Sign in" }));

  expect(onSignIn).toHaveBeenCalledWith({
    email: "ada@example.com",
    password: "lovelace",
  });
  expect(await screen.findByText(/welcome back/i)).toBeVisible();
});
```

## Async UI with the network mocked at the boundary (MSW v2)

Mock the *network*, not `fetch` and not the component's modules. Happy-path
handlers live in one shared file; a single lifecycle starts/resets/stops the
server; individual tests override a route with `server.use(...)` to drive error
and edge states.

```ts
// src/mocks/handlers.ts — happy path, shared across the suite
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/user", () => HttpResponse.json({ name: "Grace Hopper" })),
];

// src/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);

// vitest.setup.ts (or jest.setup.ts) — wired in once via the runner's setup files
import { server } from "./src/mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers()); // drop per-test overrides
afterAll(() => server.close());
```

```tsx
// UserCard.test.tsx
import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import "@testing-library/jest-dom";
import { server } from "./src/mocks/server";
import { UserCard } from "./UserCard";

test("shows the user once it loads", async () => {
  render(<UserCard />);

  expect(screen.getByRole("status")).toHaveTextContent(/loading/i);
  expect(
    await screen.findByRole("heading", { name: "Grace Hopper" }),
  ).toBeVisible();
});

test("shows an error when the request fails", async () => {
  // Override just this test's network — the base handlers stay clean.
  server.use(
    http.get("/api/user", () => new HttpResponse(null, { status: 500 })),
  );
  render(<UserCard />);

  expect(await screen.findByRole("alert")).toHaveTextContent(/couldn't load/i);
});
```

## React Native parity

Same judgments, RN-aware tools: query by role/label, drive with `user.press`/
`user.type` from `@testing-library/react-native`, await `findBy*`, and assert with
the built-in matchers (`toBeOnTheScreen` ships with RNTL — no extra import).

```tsx
import { render, screen, userEvent } from "@testing-library/react-native";
import { SignInScreen } from "./SignInScreen";

test("user signs in and sees a confirmation", async () => {
  const user = userEvent.setup();
  render(<SignInScreen />);

  await user.type(screen.getByLabelText("Email"), "ada@example.com");
  await user.press(screen.getByRole("button", { name: "Sign in" }));

  expect(await screen.findByRole("alert")).toBeOnTheScreen();
  expect(screen.getByText(/welcome back/i)).toBeVisible();
});
```
