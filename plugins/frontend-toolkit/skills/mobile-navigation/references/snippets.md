# Mobile navigation snippets

> Grounded against Context7: React Navigation 7 (`/websites/reactnavigation`),
> Expo Router on Expo SDK 54 (`/websites/expo_dev`), and React Router 7
> (`/remix-run/react-router`). Targets React 19 / React Native 0.81. Re-ground and
> update these when you bump versions.

## Typed native stack (React Navigation)

A typed param list makes every `navigate` and `route.params` checked. Params are
identity (an `id`), not the whole object — the destination fetches its own data.

```tsx
import { Button, Text } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import {
  createNativeStackNavigator,
  type NativeStackScreenProps,
} from "@react-navigation/native-stack";

// Route name -> its params. `undefined` means the route takes no params.
export type RootStackParamList = {
  Home: undefined;
  Details: { itemId: string };
};

// Make the otherwise-untyped `useNavigation()` hook aware of these routes app-wide.
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}

const Stack = createNativeStackNavigator<RootStackParamList>();

function HomeScreen({ navigation }: NativeStackScreenProps<RootStackParamList, "Home">) {
  return (
    <Button title="Open item" onPress={() => navigation.navigate("Details", { itemId: "42" })} />
  );
}

function DetailsScreen({ route }: NativeStackScreenProps<RootStackParamList, "Details">) {
  const { itemId } = route.params; // typed as string — fetch the item from this id
  return <Text>Item {itemId}</Text>;
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## Tabs as peers, a stack for drill-down (React Navigation)

Tabs are co-equal sections; a stack *inside* a tab handles push/pop within that
section. This nesting mirrors the IA — peers at the top, depth underneath.

```tsx
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

const Tab = createBottomTabNavigator();
const FeedStack = createNativeStackNavigator();

function FeedStackScreen() {
  return (
    <FeedStack.Navigator>
      <FeedStack.Screen name="FeedList" component={FeedList} />
      <FeedStack.Screen name="Post" component={Post} />
    </FeedStack.Navigator>
  );
}

function RootTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Feed" component={FeedStackScreen} />
      <Tab.Screen name="Settings" component={Settings} />
    </Tab.Navigator>
  );
}
// Type a nested navigator's params with `NavigatorScreenParams<FeedStackParamList>`
// in the parent's param list so `navigate("Feed", { screen: "Post", params: … })` is checked.
```

## Deep linking (React Navigation)

Map screens to URL paths so external links and restored state land on the right
screen. The path segment becomes a route param — same identity rule as above.

```tsx
import { Text } from "react-native";
import { NavigationContainer } from "@react-navigation/native";

const linking = {
  prefixes: ["myapp://", "https://myapp.com"],
  config: {
    screens: {
      Home: "",
      Details: "item/:itemId", // /item/42 -> route.params.itemId === "42"
    },
  },
};

export function App() {
  return (
    <NavigationContainer linking={linking} fallback={<Text>Loading…</Text>}>
      {/* navigators */}
    </NavigationContainer>
  );
}
```

## Expo Router: the same tree, file-based

Expo Router builds the navigator tree from files: `_layout.tsx` is a navigator, a
file is a screen, `[itemId].tsx` is a dynamic route whose param you read with
`useLocalSearchParams`. Linking is just the file path — no separate config.

```tsx
// app/_layout.tsx — the root stack
import { Stack } from "expo-router";
export default function RootLayout() {
  return <Stack />;
}

// app/(tabs)/_layout.tsx — a tab group: peer sections
import { Tabs } from "expo-router";
export default function TabsLayout() {
  return <Tabs />;
}

// app/item/[itemId].tsx — a dynamic route + typed param
import { Text } from "react-native";
import { Link, useLocalSearchParams } from "expo-router";

export default function Item() {
  const { itemId } = useLocalSearchParams<{ itemId: string }>();
  return <Text>Item {itemId}</Text>;
}

// Navigate by path; the link IS the deep link:
// <Link href="/item/42">Open item 42</Link>
```

Guard routes declaratively with `Stack.Protected` — a failing `guard` makes that
screen unreachable and redirects to the first available route.

```tsx
import { Stack } from "expo-router";

export function AppLayout({ isLoggedIn }: { isLoggedIn: boolean }) {
  return (
    <Stack>
      <Stack.Protected guard={!isLoggedIn}>
        <Stack.Screen name="login" />
      </Stack.Protected>
      <Stack.Protected guard={isLoggedIn}>
        <Stack.Screen name="(app)" />
      </Stack.Protected>
    </Stack>
  );
}
```

## Web parity: React Router (React-family web)

The same route tree and params-as-identity, expressed as nested route config; the
dynamic segment becomes a `useParams` value. The judgment is identical to the
native stack above — only the primitives change.

```tsx
import { createBrowserRouter, useParams } from "react-router";
import { RouterProvider } from "react-router/dom"; // v7: DOM RouterProvider lives here

function Item() {
  const { itemId } = useParams(); // the :itemId path segment
  return <p>Item {itemId}</p>;
}

const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "item/:itemId", Component: Item },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
```
