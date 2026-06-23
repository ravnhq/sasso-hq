# Forms and validation snippets

> Grounded against Context7: React 19 (`/reactjs/react.dev`), React Hook Form 7
> (`/react-hook-form/documentation`, `/react-hook-form/resolvers`), Zod 4
> (`/websites/zod_dev_v4`), and React Native 0.81 (`/facebook/react-native`).
> Re-ground and update these when you bump versions.

**Which to reach for:** use **React Hook Form + Zod** (snippet 1) for most
client-rich forms — it gives validation, dirty/touched tracking, and accessible
errors with minimal re-renders. Use a **React 19 form action** (snippet 2) when you
want the form to work before JS hydrates (server actions, MPAs, progressive
enhancement). Either way, the **schema lives in one module** (snippet 3) and the
**server re-validates** it. React Native uses the same schema via `Controller`
(snippet 4).

## 1. Schema-validated form (React Hook Form + Zod) — the workhorse

One Zod schema is the source of truth; `z.infer` gives the type; `zodResolver` wires
it to the form; errors render accessibly (`aria-invalid` + `aria-describedby` +
`role="alert"`).

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// One schema = validation + types. (Zod 4: top-level z.email(); `error` for messages.)
const SignupSchema = z.object({
  email: z.email({ error: "Enter a valid email." }),
  password: z.string().min(8, { error: "At least 8 characters." }),
});
type SignupValues = z.infer<typeof SignupSchema>;

export function SignupForm({ onSignup }: { onSignup: (v: SignupValues) => Promise<void> }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<SignupValues>({
    resolver: zodResolver(SignupSchema),
    mode: "onTouched", // validate after first blur, then re-validate on change
  });

  async function onSubmit(values: SignupValues) {
    try {
      await onSignup(values);
    } catch {
      // Surface a server error where field errors live.
      setError("root.server", { message: "Could not sign up. Try again." });
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        aria-invalid={errors.email ? "true" : "false"}
        aria-describedby={errors.email ? "email-error" : undefined}
        {...register("email")}
      />
      {errors.email && <p id="email-error" role="alert">{errors.email.message}</p>}

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        aria-invalid={errors.password ? "true" : "false"}
        aria-describedby={errors.password ? "password-error" : undefined}
        {...register("password")}
      />
      {errors.password && <p id="password-error" role="alert">{errors.password.message}</p>}

      {errors.root?.server && <p role="alert">{errors.root.server.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Signing up…" : "Sign up"}
      </button>
    </form>
  );
}
```

## 2. Platform-native form action (React 19) — progressive enhancement

When the form should work before JS hydrates (server actions, MPAs), use the `action`
prop with `useActionState`; a child component reads `useFormStatus` for the pending
state. Re-validate the same schema on the server.

This `SignupForm` is a Client Component (it calls `useActionState`/`useFormStatus`), so
the server action must live in its own `"use server"` module and be **imported** — an
inline `"use server"` function is only allowed inside a Server Component, not here.

```tsx
import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { signupAction } from "./actions"; // server action, imported from a "use server" module

function SubmitButton() {
  const { pending } = useFormStatus(); // must render *inside* the <form>
  return (
    <button type="submit" disabled={pending}>
      {pending ? "Signing up…" : "Sign up"}
    </button>
  );
}

export function SignupForm() {
  const [error, action] = useActionState(signupAction, null);

  return (
    // `required` + `type="email"` give a no-JS validation fallback; the server is authoritative.
    <form action={action}>
      <label htmlFor="email">Email</label>
      <input id="email" name="email" type="email" required />

      <label htmlFor="password">Password</label>
      <input id="password" name="password" type="password" required />

      {error && <p role="alert">{error}</p>}
      <SubmitButton />
    </form>
  );
}
```

```ts
// actions.ts — a "use server" module. The Client Component imports signupAction from here.
"use server";
import { SignupSchema } from "./schema"; // same Zod schema, reused

export async function signupAction(
  _prev: string | null,
  formData: FormData,
): Promise<string | null> {
  // Re-validate with the SAME schema on the server — this check is the contract.
  const parsed = SignupSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return "Check the highlighted fields.";
  // await createUser(parsed.data);
  return null;
}
```

## 3. One schema, validated on both sides

Put the schema in its own module and import it everywhere — the web form, the React
Native form, and the server all share it. The client check is fast feedback; the
server check is the contract.

```ts
// schema.ts — imported by every form here and by the server.
import { z } from "zod";

export const SignupSchema = z.object({
  email: z.email({ error: "Enter a valid email." }),
  password: z.string().min(8, { error: "At least 8 characters." }),
});
export type SignupValues = z.infer<typeof SignupSchema>;
```

```ts
// server: never trust the client — re-run the same schema.
import { SignupSchema } from "./schema";

export async function handleSignup(body: unknown) {
  const parsed = SignupSchema.safeParse(body);
  if (!parsed.success) {
    // Map issues to { field: message } for the client to render.
    const fieldErrors: Record<string, string> = {};
    for (const issue of parsed.error.issues) {
      fieldErrors[String(issue.path[0])] = issue.message;
    }
    return { ok: false as const, fieldErrors };
  }
  // parsed.data is fully typed as SignupValues.
  // await createUser(parsed.data);
  return { ok: true as const };
}
```

## 4. React Native form (React Hook Form `Controller`)

RN has no `<form>`; drive each `TextInput` with `Controller` against the same schema.
Set the keyboard per field, wire `returnKeyType` + `onSubmitEditing` to move focus,
and label every input for assistive tech.

```tsx
import { useRef } from "react";
import { View, Text, TextInput, Button } from "react-native";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { SignupSchema, type SignupValues } from "./schema";

export function SignupForm({ onSignup }: { onSignup: (v: SignupValues) => Promise<void> }) {
  const passwordRef = useRef<TextInput>(null);
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupValues>({
    resolver: zodResolver(SignupSchema),
    defaultValues: { email: "", password: "" }, // every field controlled from first render
    mode: "onTouched",
  });

  return (
    <View>
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            accessibilityLabel="Email"
            keyboardType="email-address" // RN 0.71+: also `inputMode="email"`
            autoCapitalize="none"
            autoComplete="email"
            returnKeyType="next"
            onSubmitEditing={() => passwordRef.current?.focus()}
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
          />
        )}
      />
      {errors.email && <Text accessibilityRole="alert">{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            ref={passwordRef}
            accessibilityLabel="Password"
            secureTextEntry
            returnKeyType="done"
            onSubmitEditing={handleSubmit(onSignup)}
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
          />
        )}
      />
      {errors.password && <Text accessibilityRole="alert">{errors.password.message}</Text>}

      <Button
        title={isSubmitting ? "Signing up…" : "Sign up"}
        onPress={handleSubmit(onSignup)}
      />
    </View>
  );
}
```
