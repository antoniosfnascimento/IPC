# Functional Requirements (CityFlow MVP)

This table summarises the CityFlow architectural documentation as a *Product Backlog* focused on the Minimum Viable Product (MVP), prioritising the core of technical accessibility over business abstractions.

| ID | Feature | Technical description | MVP priority |
| :---: | :--- | :--- | :---: |
| **RF-01** | Accessibility profile selection | The frontend keeps a profile state (via Context API) to switch between "Wheelchair", "Senior", "Colour-blind". Every profile emits a strict JSON validated by Pydantic on the backend. | **Must-have** |
| **RF-02** | Dynamic routing engine | The backend (FastAPI + OSMnx) receives the coordinates and applies the mathematical heuristic (*edge weights*) computing the path on the graph with Bellman-Ford in less than two seconds. | **Must-have** |
| **RF-03** | "Low cognitive load" map interface | Use Leaflet / react-leaflet with conditional rendering to hide the underlying street layer, leaving only the calculated route polyline visible (Easy-Read mode). | **Must-have** |
| **RF-04** | Submission and re-routing for temporary barriers | A frontend endpoint via `navigator.geolocation` intercepts a graph node and sets `is_blocked = True` temporarily, triggering a re-route (active crowdsourcing). | **Must-have** |
| **RF-05** | Haptic and sonic sensory feedback | Invoke `navigator.vibrate(200)` and `window.speechSynthesis.speak()` whenever the user approaches a node that requires a direction change greater than 45 degrees. | **Must-have** |
| **RF-06** | Native high-contrast toggle | Global Floating Action Button (`z-50`) that updates the native CSS theme variables, switching the basemap layer to `dark_matter` and enforcing high contrast (ratio > 7:1). | **Must-have** |
| **RF-07** | Fail-safe parsing (sanitiser) | The backend must not return 500 if `width` or `incline` arrive malformed (e.g. string "narrow") from OpenStreetMap. It must fall back to a safe default. | **Must-have** |
| **RF-08** | Real-time GPS turn-by-turn navigation | Track the user's coordinates with `watchPosition` to drive a moving marker and rotate the map according to the device compass. | **Nice-to-have** |
| **RF-09** | SOS button | A quick PWA-embedded button to dial 112 or a pre-defined contact when the wheelchair gets stuck or something urgent happens. | **Nice-to-have** |
| **RF-10** | In-memory map pre-caching | The server processes the GraphML file on startup (`startup_event`) loading the 1.5 km radius into RAM, avoiding RAM spikes and long waits on each request. | **Must-have** |

### MVP decision criteria
*   **Must-have:** Structural components and core differentiating logic essential for the proof of concept facing the jury / faculty. Without them, the project is not CityFlow.
*   **Nice-to-have:** Excellent quality-of-life improvements for PWA / mobile that, on the other hand, demand significant technical overhead (live GPS tracking requires altimetric error filtering, so it is not vital for the conceptual prototype where the *generated route on screen* is enough to prove the point).
