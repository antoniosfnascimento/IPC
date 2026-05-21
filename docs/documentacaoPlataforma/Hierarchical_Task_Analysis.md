# Hierarchical Task Analysis (HTA) — CityFlow MVP

This document applies the *Hierarchical Task Analysis* methodology to the main value journey of CityFlow. The goal is to identify every friction point where the Frontend or the Backend can fail the user, defining the corresponding error handling.

## Main task (Macro-Task) — Level 0
**0. Plan a safe inclusive route** (Goal: travel from A to B without crossing intolerable physical barriers).

| HTA | Sub-task | User action (Frontend) | System process (Backend / App) | Error condition and handling |
| :---: | :--- | :--- | :--- | :--- |
| **1.** | **Set base profile** | Clicks a *Card* or toggler ("Wheelchair / Visual / Senior"). | Loads the mathematical constants (constraints) into the global app state (e.g. `max_incline: 0.08`). | **Error (1.1):** User skips the profile.<br>**Handling:** Submit button stays *disabled* and a visual alert asks for a profile. |
| **2.** | **Enter origin coordinates** | Types in the "Origin" field or clicks the GPS "My location" button. | The system acquires and sanitises the string via a geocoding provider (Nominatim) or `navigator.geolocation`. Pydantic casts to `[lat, lon]`. | **Error (2.1):** GPS permission denied by the browser.<br>**Handling:** Fallback to manual text input with a friendly message: "Please type your origin." The app must not crash. |
| **3.** | **Enter destination** | Types in the "Destination" field or taps the Leaflet map. | Translates the text into a precise geographic coordinate. | **Error (3.1):** Destination outside the pre-loaded RAM mesh for the active city (radius > 1.5 km).<br>**Handling:** FastAPI replies with 400. The frontend says: "Destination outside the currently mapped metropolitan area." |
| **4.** | **Submit (start API request)** | Triggers the "Calculate" button (target 44×44 px — WCAG 2.5.5). | Frontend sends the populated POST model to the backend, including the active city slug. | **Error (4.1):** Client-side Internet failure.<br>**Handling:** Toast "Network connection lost", stopping the loading spinner. |
| **5.** | **Compute graph variables** | Analytical waiting (spinner). | The Python routing engine runs Bellman-Ford on `NetworkX`, weighting the edges of the selected city graph. | **Error (5.1):** OSM tags are corrupted and break the math.<br>**Handling:** `FeatureSanitizer.parse_float()` forces safe defaults. Error silenced for the user. |
| **6.** | **Check barriers (edge case)** | Transparent / immediate (during step 5). | Bellman-Ford tries to connect origin (node U) and destination (node V) through finite-weight edges. Destination is physically "ringed by stairs". | **Error (6.1):** Isolated dead-end (no solution under the cap).<br>**Handling:** FastAPI returns 424 Failed Dependency. The client says: "Destination physically impossible or isolated under this profile." |
| **7.** | **Sensory success rendering** | The user observes the rendered route. | Leaflet draws the thick filled polyline. The app announces "Start of trip" through TTS. | **Error (7.1):** Route overlaps non-pedestrian streets and confuses the Leaflet base.<br>**Handling:** Correctly indexed Leaflet layers (z-index) so the polyline is always opaque on top. |

*Methodological note:* If step 6 does not fail, the macro-task 0 is considered successfully completed (the user can now start the physical journey).
