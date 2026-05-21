# Information Architecture (CityFlow MVP)

This document dictates the hierarchical structure and content organisation of the **CityFlow** frontend. The table is the blueprint from which web developers build the views (React components) and the routing flow.

To keep focus on the MVP and usability (reduced cognitive load), the app follows an aggressive single-page architecture with mobile modals / drawers instead of separate pages, ensuring the map never leaves the user's peripheral view.

| Logical name (screen / base component) | What it shows / visual components | User actions (`onClick`, `onSubmit`) | Navigation (where the user moves to) |
| :--- | :--- | :--- | :--- |
| **`MapView` (parent / Home)** | The Leaflet/map component (100% viewport `h-screen w-screen`). Shows light/dark basemaps depending on profile. | Free pan, `zoom-in`, `zoom-out`. | Keeps the user on this screen at all times. Triggers the overlay child screens listed below. |
| **`Floating UI Layer`** (z-index above the map) | "Centre GPS" button, "Dark mode / High contrast" toggle, circular profile icon on top. | Toggle dynamic contrast; centre location. Click on the profile photo/icon. | Expand profile modals or call APIs without leaving the page. The profile icon opens the **`ProfileSettingsModal`**. |
| **`RoutePlannerPanel`** (flexible floating footer) | Bottom sheet (drawer from the bottom). Origin text input, destination text input. `[ Calculate route ]` button (min 44×44 px). | Fill text inputs; trigger the "Calculate" button. `onClick` on an empty area of the map injects the reverse-geocoded string into the destination field. | On submit, the UI stays put, calls the backend, shows the `LoadingSpinner` (WCAG `aria-live`), and transitions the UI state to **`ActiveNavigationOverlay`**. |
| **`ProfileSettingsModal`** (focused modal) | Radio buttons (single choice): "Wheelchair", "Low vision", "Senior". Sliders for hard constraints: "Path width" (0.5 m to 2 m), "Max slope". | Tweak heuristic variables and press `[ Save profile ]`. | Show toast "Profile applied". Close the modal automatically. Focus returns to **`MapView`**. |
| **`ActiveNavigationOverlay`** (Easy-Read trip mode) | Hides every text input. Limits visual load to: a tall top bar with the next direction ("Turn in 50 m") and a square button with the manoeuvre arrow. The red base button `[ REPORT OBSTACLE ]` appears. | Read the indication. Follow the thick polyline. SOS via *Report*. | Reaching the destination returns to the empty **`RoutePlannerPanel`**. The Report button raises the toast "Re-routing alternative" via the crowdsourcing API. |
| **`ErrorFeedbackToast`** (cross-cutting) | Small balloon. Yellow / red depending on severity (WCAG). Surfaces Pydantic failures naturally. E.g. "Warning: no route for this profile (424)". | Dismiss `onClick` ('X'). | Does not transition. Auto-dismiss after 3000 ms. |

### Frontend notes (React.js)
Given the PWA / accessibility scope, developers should never use plain `<a href="/settings">` links between stations. The phone screen must never blink or wipe on a hard navigation.

`MapView` is the permanent root (`/`), and every panel slides smoothly along the Z axis from the bottom of the phone towards the user's thumb (Thumb-zone Design).
